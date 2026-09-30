"""Report the S3 restore testing results to Slack (TEC-2063).

Runs as the restore-check-s3-report Lambda durable function, invoked by
an EventBridge schedule at noon on the 1st - hours after the restore
testing plans started restoring every protected bucket into scratch
buckets and restore-check-s3-validate stamped each job with a verdict.
One linear durable execution: list the restore jobs both plans produced,
suspend (free of charge) until every job is finished and validated (or
give up after ~6 hours), then post one Slack table covering them all.

The cross-job assertion lives here, where the per-job validator cannot
see it: every protected bucket must have produced a restore job. A bucket
AWS Backup silently skipped (no eligible recovery point, dropped from the
selection) is a FAIL row, not a missing row. The Sydney plan runs
monthly; the Melbourne air-gapped plan quarterly, so Melbourne rows are
only expected in those months - but any Melbourne jobs that do exist
(e.g. a hand-started run) are always reported.

A Sentry cron monitor (restore-check-s3) is the dead-man behind this
reporter, same pattern as the other checks: check in in_progress at the
start and ok/error at the end, best-effort. Durable execution discipline
as db-lambda.py: side effects only inside @durable_step, secrets read
within steps and never checkpointed.

Configuration from environment variables set by OpenTofu:
PRIMARY_PLAN_ARN, PRIMARY_REGION, AIRGAP_PLAN_ARN, AIRGAP_REGION,
AIRGAP_MONTHS (comma-separated month numbers), PROTECTED_BUCKETS (JSON),
WEBHOOK_PARAMETER, SENTRY_PARAMETER.
"""

import json
import os
import time
import urllib.request
import uuid
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import boto3
import report
from aws_durable_execution_sdk_python import (
    DurableContext,
    durable_execution,
    durable_step,
)
from aws_durable_execution_sdk_python.config import Duration

PRIMARY_PLAN_ARN = os.environ["PRIMARY_PLAN_ARN"]
PRIMARY_REGION = os.environ["PRIMARY_REGION"]
AIRGAP_PLAN_ARN = os.environ["AIRGAP_PLAN_ARN"]
AIRGAP_REGION = os.environ["AIRGAP_REGION"]
AIRGAP_MONTHS = [int(month) for month in os.environ["AIRGAP_MONTHS"].split(",")]
PROTECTED_BUCKETS = json.loads(os.environ["PROTECTED_BUCKETS"])
WEBHOOK_PARAMETER = os.environ["WEBHOOK_PARAMETER"]
SENTRY_PARAMETER = os.environ["SENTRY_PARAMETER"]

PLANS = {
    PRIMARY_REGION: {"arn": PRIMARY_PLAN_ARN, "label": "Sydney"},
    AIRGAP_REGION: {"arn": AIRGAP_PLAN_ARN, "label": "Melbourne air-gap"},
}

TERMINAL_STATUSES = ("COMPLETED", "ABORTED", "FAILED")
FINAL_VALIDATIONS = ("SUCCESSFUL", "FAILED", "TIMED_OUT")  # not VALIDATING/absent

# The plans start their jobs at 5-6AM and S3 restores take minutes to
# hours; poll from noon until everything is finished and validated, give
# up after ~6 more hours.
LOOKBACK_SECONDS = 24 * 3600
POLL_SECONDS = 600
MAX_POLLS = 36

REPORT_TITLE = "Monthly S3 restore check"
REPORT_NAME = "S3 restore check"


# --- Steps (each checkpointed; never re-executed on replay) -------------------


@durable_step
def window(step_context) -> dict:
    """The reporting window and month, read from the clock exactly once."""
    now = time.time()
    month = datetime.fromtimestamp(now, tz=ZoneInfo("Australia/Melbourne")).month
    return {"since": now - LOOKBACK_SECONDS, "month": month}


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
def list_jobs(step_context, region: str, plan_arn: str, since: float) -> list[dict]:
    """This plan's restore jobs in the window, trimmed to what the report
    needs (checkpointed, so JSON-safe and small)."""
    backup = boto3.client("backup", region_name=region)
    jobs = []
    paginator = backup.get_paginator("list_restore_jobs")
    for page in paginator.paginate(
        ByRestoreTestingPlanArn=plan_arn,
        ByCreatedAfter=datetime.fromtimestamp(since, tz=timezone.utc),
    ):
        for job in page["RestoreJobs"]:
            jobs.append(
                {
                    "bucket": job.get("SourceResourceArn", "").split(":::")[-1],
                    "status": job["Status"],
                    "status_message": job.get("StatusMessage", ""),
                    "validation": job.get("ValidationStatus"),
                    "validation_message": job.get("ValidationStatusMessage", ""),
                    "bytes": job.get("BackupSizeInBytes"),
                    "created": job["CreationDate"].timestamp(),
                }
            )
    return jobs


@durable_step
def post_report(step_context, results: dict, outcome: str, run_url: str) -> None:
    report.post(
        webhook(),
        report.build_payload(
            results, outcome, run_url=run_url, title=REPORT_TITLE, name=REPORT_NAME
        ),
    )


@durable_step
def post_crash_alert(step_context, error: str, run_url: str) -> None:
    """Best-effort: an undeliverable courtesy alert must not replace the
    crash it is reporting as the execution's own error."""
    step_context.logger.error(f"S3 restore check reporter crashed: {error}")
    try:
        report.post(
            webhook(),
            report.build_payload(
                None, "FAIL", run_url=run_url, title=REPORT_TITLE, name=REPORT_NAME
            ),
        )
    except Exception as post_error:
        step_context.logger.error(f"Crash alert could not be posted: {post_error}")


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


def settled(jobs_by_region: dict[str, list[dict]]) -> bool:
    """True once no job can change further: every job is terminal, and
    every completed job carries a validation verdict. Buckets with no job
    at all never will get one (the plans start within an hour of 5AM), so
    they do not hold the report open."""
    for jobs in jobs_by_region.values():
        for job in jobs:
            if job["status"] not in TERMINAL_STATUSES:
                return False
            if job["status"] == "COMPLETED" and job["validation"] not in FINAL_VALIDATIONS:
                return False
    return True


def bucket_check(region_label: str, bucket: str, job: dict | None) -> dict:
    """One report row: this bucket's newest restore job in this region."""
    label = f"{bucket} ({region_label})"
    if job is None:
        return {
            "label": label,
            "status": "FAIL",
            "value": "",
            "note": "no restore job was created",
        }
    size = report.human_size(job["bytes"]) if job.get("bytes") else ""
    if job["status"] != "COMPLETED":
        note = f"restore job {job['status']}"
        if job["status_message"]:
            note += f": {job['status_message']}"
        return {"label": label, "status": "FAIL", "value": size, "note": note}
    if job["validation"] == "SUCCESSFUL":
        return {
            "label": label,
            "status": "PASS",
            "value": size,
            "note": "restored and validated",
        }
    if not job["validation"]:
        return {
            "label": label,
            "status": "FAIL",
            "value": size,
            "note": "restored but never validated",
        }
    return {
        "label": label,
        "status": "FAIL",
        "value": size,
        "note": job["validation_message"] or f"validation {job['validation']}",
    }


def build_results(jobs_by_region: dict[str, list[dict]], month: int) -> dict:
    """The report rows: every protected bucket in every region that was
    expected to test this month (plus any region that ran anyway)."""
    checks = []
    for region, plan in PLANS.items():
        jobs = jobs_by_region.get(region, [])
        expected = region == PRIMARY_REGION or month in AIRGAP_MONTHS
        for bucket in PROTECTED_BUCKETS:
            newest = max(
                (job for job in jobs if job["bucket"] == bucket),
                key=lambda job: job["created"],
                default=None,
            )
            # In a region with no run due this month, report only the jobs
            # that exist (a hand-started test), not the absent siblings.
            if newest is None and not expected:
                continue
            checks.append(bucket_check(plan["label"], bucket, newest))
    outcome = "PASS" if all(check["status"] == "PASS" for check in checks) else "FAIL"
    return {"outcome": outcome, "checks": checks}


def console_url() -> str:
    """The Backup console's restore jobs page, for the report footer."""
    return (
        f"https://{PRIMARY_REGION}.console.aws.amazon.com/backup/home"
        f"?region={PRIMARY_REGION}#/jobs/restore"
    )


# --- The durable execution -----------------------------------------------------


@durable_execution
def handler(event, context: DurableContext):
    checkin_id = None
    try:
        checkin_id = context.step(open_checkin())
        bounds = context.step(window())

        jobs_by_region = {}
        for _ in range(MAX_POLLS):
            jobs_by_region = {
                region: context.step(list_jobs(region, plan["arn"], bounds["since"]))
                for region, plan in PLANS.items()
            }
            if settled(jobs_by_region):
                break
            context.wait(Duration.from_seconds(POLL_SECONDS))
        # Falling out of the loop unsettled is fine: unfinished or
        # unvalidated jobs become FAIL rows.

        results = build_results(jobs_by_region, bounds["month"])
        context.step(post_report(results, results["outcome"], console_url()))
        context.step(
            close_checkin(checkin_id, "ok" if results["outcome"] == "PASS" else "error")
        )
        return results

    except Exception as error:
        # Close the check-in before attempting Slack: Sentry is the alert
        # of record, so an unreachable webhook must not stop it being
        # told (an unclosed check-in only surfaces hours later, as a
        # monitor timeout).
        context.step(close_checkin(checkin_id, "error"))
        context.step(post_crash_alert(str(error), console_url()))
        raise
