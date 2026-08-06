"""Orchestrate the monthly database restore check (TEC-2065).

Runs as the restore-check-db Lambda durable function, invoked monthly by
an EventBridge schedule (and by hand via `aws lambda invoke` on the live
alias - see docs/restore-check.md). One linear durable execution: launch
the check as a Fargate task, suspend (free of charge) until the task
stops, pull its results JSON out of the task's log stream, and post the
Slack report. Every observable failure funnels into the except handler,
which still posts to Slack.

A Sentry cron monitor is the backstop behind all of that: the execution
checks in in_progress before launching and ok/error when it finishes, so
Sentry alerts when the check never starts (schedule disabled, invoke
lost), dies before finishing, or reports a failure. Check-ins are
best-effort - a Sentry outage must never fail an otherwise good run; the
worst case is a false "missed" alert, which is itself a useful signal
that the monitoring path broke. The monitor and its alert rule are
defined next to the EventBridge schedule in
infra/tofu/restore-check/foundations/db.tf; this handler only checks in.

Durable execution discipline: everything with a side effect - each AWS
call, even reading the clock - happens inside a @durable_step, so replays
after a suspension never repeat completed work. Code outside the steps is
deterministic. Step results are checkpointed, so no step returns a
secret: the Slack webhook and the Sentry URL are read and used entirely
within their steps.

Configuration comes from environment variables set by OpenTofu (see
infra/tofu/restore-check/foundations): CLUSTER, TASK_DEFINITION,
SUBNET_ID, SECURITY_GROUP_ID, LOG_GROUP, CONTAINER_NAME, STREAM_PREFIX,
WEBHOOK_PARAMETER, SENTRY_PARAMETER.
"""

import json
import os
import time
import urllib.parse
import urllib.request
import uuid

import boto3
from aws_durable_execution_sdk_python import (
    DurableContext,
    durable_execution,
    durable_step,
)
from aws_durable_execution_sdk_python.config import Duration

import report

CLUSTER = os.environ["CLUSTER"]
TASK_DEFINITION = os.environ["TASK_DEFINITION"]
SUBNET_ID = os.environ["SUBNET_ID"]
SECURITY_GROUP_ID = os.environ["SECURITY_GROUP_ID"]
LOG_GROUP = os.environ["LOG_GROUP"]
CONTAINER_NAME = os.environ["CONTAINER_NAME"]
STREAM_PREFIX = os.environ["STREAM_PREFIX"]
WEBHOOK_PARAMETER = os.environ["WEBHOOK_PARAMETER"]
SENTRY_PARAMETER = os.environ["SENTRY_PARAMETER"]
REGION = os.environ["AWS_REGION"]

RESULTS_MARKER = "===RESTORE-CHECK-RESULTS==="

# The check typically takes ~10 minutes; its in-container timeout fires at
# 90. Give up just after that, so the container's own failsafe is always
# the first to act and this loop only mops up ECS-level wedges.
POLL_SECONDS = 60
MAX_POLLS = 100


# --- Steps (each checkpointed; never re-executed on replay) -------------------


@durable_step
def sweep_leftovers(step_context) -> dict:
    """Stop stale tasks a dead run left behind; spot a genuinely live one."""
    ecs = boto3.client("ecs")
    arns = ecs.list_tasks(cluster=CLUSTER, desiredStatus="RUNNING")["taskArns"]
    if not arns:
        return {"in_flight": False}
    in_flight = False
    for task in ecs.describe_tasks(cluster=CLUSTER, tasks=arns)["tasks"]:
        age = time.time() - task["createdAt"].timestamp()
        if age > POLL_SECONDS * MAX_POLLS:
            step_context.logger.info(f"Stopping stale task {task['taskArn']}")
            ecs.stop_task(cluster=CLUSTER, task=task["taskArn"],
                          reason="stale restore check task (swept by a new run)")
        else:
            in_flight = True
    return {"in_flight": in_flight}


@durable_step
def open_checkin(step_context) -> str | None:
    """Tell Sentry the run started; returns the check-in id to close with."""
    checkin_id = uuid.uuid4().hex
    ok = sentry_checkin(step_context, checkin_id, "in_progress")
    return checkin_id if ok else None


@durable_step
def close_checkin(step_context, checkin_id: str | None, status: str) -> None:
    if checkin_id:
        sentry_checkin(step_context, checkin_id, status)


@durable_step
def run_task(step_context) -> str:
    """Launch the check task; returns its ARN."""
    response = boto3.client("ecs").run_task(
        cluster=CLUSTER,
        taskDefinition=TASK_DEFINITION,
        count=1,
        launchType="FARGATE",
        networkConfiguration={
            "awsvpcConfiguration": {
                "subnets": [SUBNET_ID],
                "securityGroups": [SECURITY_GROUP_ID],
                "assignPublicIp": "ENABLED",
            }
        },
    )
    if response["failures"]:
        raise RuntimeError(f"RunTask failed: {response['failures']}")
    return response["tasks"][0]["taskArn"]


@durable_step
def task_state(step_context, task_arn: str) -> dict:
    tasks = boto3.client("ecs").describe_tasks(
        cluster=CLUSTER, tasks=[task_arn]
    )["tasks"]
    if not tasks:
        return {"status": "MISSING", "exit_code": None, "reason": "task not found"}
    task = tasks[0]
    containers = task.get("containers", [])
    return {
        "status": task["lastStatus"],
        "exit_code": containers[0].get("exitCode") if containers else None,
        "reason": task.get("stoppedReason", ""),
    }


@durable_step
def stop_task(step_context, task_arn: str, reason: str) -> None:
    """Best-effort stop: never raises, so cleanup cannot mask the real error."""
    try:
        boto3.client("ecs").stop_task(cluster=CLUSTER, task=task_arn, reason=reason)
    except Exception as error:  # already stopped / already reaped
        step_context.logger.info(f"StopTask skipped: {error}")


@durable_step
def fetch_results(step_context, task_arn: str) -> dict | None:
    """The results JSON db-check.py printed, read back from the log stream."""
    logs = boto3.client("logs")
    try:
        events = logs.get_log_events(
            logGroupName=LOG_GROUP,
            logStreamName=log_stream(task_arn),
            startFromHead=False,  # the marker is at the very end of the run
        )["events"]
    except logs.exceptions.ResourceNotFoundException:
        return None  # the container never logged at all
    lines = [event["message"] for event in events]
    for index, line in enumerate(lines):
        if RESULTS_MARKER in line and index + 1 < len(lines):
            try:
                return json.loads(lines[index + 1])
            except json.JSONDecodeError:
                return None
    return None


@durable_step
def post_report(step_context, results: dict | None, outcome: str, run_url: str) -> None:
    report.post(webhook(), report.build_payload(results, outcome, run_url=run_url))


@durable_step
def post_crash_alert(step_context, error: str, run_url: str) -> None:
    step_context.logger.error(f"Restore check crashed: {error}")
    report.post(webhook(), report.build_payload(None, "FAIL", run_url=run_url))


# --- Helpers -------------------------------------------------------------------


def webhook() -> str:
    """Read the Slack webhook. Called only inside posting steps, so the
    secret is used within a step but never checkpointed as a result."""
    return boto3.client("ssm").get_parameter(
        Name=WEBHOOK_PARAMETER, WithDecryption=True
    )["Parameter"]["Value"]


def sentry_checkin(step_context, checkin_id, status) -> bool:
    """POST a check-in to the Sentry cron monitor. Best-effort by design."""
    body = {"check_in_id": checkin_id, "status": status}
    try:
        url = boto3.client("ssm").get_parameter(
            Name=SENTRY_PARAMETER, WithDecryption=True
        )["Parameter"]["Value"]
        request = urllib.request.Request(
            url,
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=10):
            pass
        return True
    except Exception as error:
        step_context.logger.error(f"Sentry check-in failed: {error}")
        return False


def log_stream(task_arn: str) -> str:
    """The awslogs driver names streams <prefix>/<container>/<task id>."""
    return f"{STREAM_PREFIX}/{CONTAINER_NAME}/{task_arn.split('/')[-1]}"


def console_url(task_arn: str | None) -> str:
    """A console deep link to the task's log stream (or the group)."""

    def encode(part: str) -> str:
        # The console URL fragment double-encodes, with $ in place of %.
        return urllib.parse.quote(part, safe="").replace("%", "$25")

    url = (
        f"https://{REGION}.console.aws.amazon.com/cloudwatch/home"
        f"?region={REGION}#logsV2:log-groups/log-group/{encode(LOG_GROUP)}"
    )
    if task_arn:
        url += f"/log-events/{encode(log_stream(task_arn))}"
    return url


# --- The durable execution -----------------------------------------------------


@durable_execution
def handler(event, context: DurableContext):
    task_arn = None
    checkin_id = None
    try:
        # Skip before checking in: the in-flight run owns the open check-in,
        # and if it silently dies Sentry must still see its run time out.
        if context.step(sweep_leftovers())["in_flight"]:
            return {"outcome": "SKIPPED", "note": "a check task is already running"}

        checkin_id = context.step(open_checkin())
        task_arn = context.step(run_task())

        state = {}
        for _ in range(MAX_POLLS):
            state = context.step(task_state(task_arn))
            if state["status"] in ("STOPPED", "MISSING"):
                break
            context.wait(Duration.from_seconds(POLL_SECONDS))
        else:
            context.step(stop_task(task_arn, "restore check gave up waiting"))
            state = {"status": "GAVE_UP", "exit_code": None, "reason": ""}

        # exit 0 pass, 1 fail, 124 the in-container timeout fired; the
        # results JSON is what the report is actually built from, and its
        # absence alone means FAIL regardless of the exit code.
        results = None
        if state["status"] == "STOPPED":
            for _ in range(6):
                results = context.step(fetch_results(task_arn))
                if results:
                    break
                context.wait(Duration.from_seconds(10))  # log delivery lag

        outcome = results["outcome"] if results else "FAIL"
        context.step(post_report(results, outcome, console_url(task_arn)))
        context.step(close_checkin(checkin_id, "ok" if outcome == "PASS" else "error"))
        return {
            "outcome": outcome,
            "task": task_arn,
            "exit_code": state.get("exit_code"),
        }

    except Exception as error:
        if task_arn:
            context.step(stop_task(task_arn, "restore check orchestration failed"))
        context.step(post_crash_alert(str(error), console_url(task_arn)))
        context.step(close_checkin(checkin_id, "error"))
        raise
