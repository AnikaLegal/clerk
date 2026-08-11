"""Assert that the AWS Backup snapshots of the S3 buckets land (TEC-2063).

Runs daily as the backup-check-s3 Lambda: for every protected bucket
(the list comes from the infra/tofu/backup root, via the environment),
the newest completed recovery point must be fresh in the primary region
AND its copy must have landed in the air-gapped Melbourne vault. Healthy
runs are silent apart from an ok check-in to the backup-check-s3 Sentry
cron monitor; any gap posts a Slack alert and checks in error. If this
Lambda itself silently stops, the monitor misses its daily check-in and
Sentry alerts - the same dead-man pattern as the restore checks.

This is the "backups exist" layer; the restore testing plans and their
validators (see docs/restore-check.md) are the "backups restore" layer.

Configuration from environment variables set by OpenTofu:
PROTECTED_BUCKETS (JSON list), PRIMARY_REGION, COPY_REGION,
PRIMARY_THRESHOLD_HOURS, COPY_THRESHOLD_HOURS, WEBHOOK_PARAMETER,
SENTRY_PARAMETER.
"""

import json
import logging
import os
import time
import urllib.request
import uuid

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

PROTECTED_BUCKETS = json.loads(os.environ["PROTECTED_BUCKETS"])
PRIMARY_REGION = os.environ["PRIMARY_REGION"]
COPY_REGION = os.environ["COPY_REGION"]
PRIMARY_THRESHOLD_HOURS = float(os.environ["PRIMARY_THRESHOLD_HOURS"])
COPY_THRESHOLD_HOURS = float(os.environ["COPY_THRESHOLD_HOURS"])
WEBHOOK_PARAMETER = os.environ["WEBHOOK_PARAMETER"]
SENTRY_PARAMETER = os.environ["SENTRY_PARAMETER"]


def newest_point_age_hours(client, bucket: str) -> float | None:
    """Age of the newest completed recovery point, or None if there is none."""
    newest = None
    paginator = client.get_paginator("list_recovery_points_by_resource")
    for page in paginator.paginate(ResourceArn=f"arn:aws:s3:::{bucket}"):
        for point in page["RecoveryPoints"]:
            if point.get("Status") != "COMPLETED":
                continue
            if newest is None or point["CreationDate"] > newest:
                newest = point["CreationDate"]
    if newest is None:
        return None
    return (time.time() - newest.timestamp()) / 3600


def find_problems() -> list[str]:
    problems = []
    for region, threshold, label in (
        (PRIMARY_REGION, PRIMARY_THRESHOLD_HOURS, "primary vault"),
        (COPY_REGION, COPY_THRESHOLD_HOURS, "air-gapped copy"),
    ):
        client = boto3.client("backup", region_name=region)
        for bucket in PROTECTED_BUCKETS:
            age = newest_point_age_hours(client, bucket)
            if age is None:
                problems.append(f"`{bucket}`: no completed recovery point "
                                f"in the {label} ({region})")
            elif age > threshold:
                problems.append(f"`{bucket}`: newest point in the {label} "
                                f"({region}) is {age:.0f}h old (limit {threshold:.0f}h)")
    return problems


# --- Reporting -----------------------------------------------------------------


def parameter(name: str) -> str:
    return boto3.client("ssm").get_parameter(Name=name, WithDecryption=True)[
        "Parameter"
    ]["Value"]


def alert_slack(problems: list[str]) -> None:
    lines = "\n".join(f"- {problem}" for problem in problems)
    payload = {
        "text": "S3 backup landing check FAILED - please investigate.",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": ":x: S3 backup landing check",
                    "emoji": True,
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*FAILED* - AWS Backup recovery points are missing "
                    f"or stale. Please investigate.\n{lines}",
                },
            },
        ],
    }
    request = urllib.request.Request(
        parameter(WEBHOOK_PARAMETER),
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=30):
        pass


def sentry_checkin(status: str) -> None:
    """Close out the cron monitor. Best-effort: a Sentry outage must never
    fail the run - the worst case is a false "missed" alert."""
    body = {"check_in_id": uuid.uuid4().hex, "status": status}
    try:
        request = urllib.request.Request(
            parameter(SENTRY_PARAMETER),
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=10):
            pass
    except Exception as error:
        logger.error(f"Sentry check-in failed: {error}")


# --- Entry point -----------------------------------------------------------------


def handler(event, context):
    try:
        problems = find_problems()
    except Exception:
        sentry_checkin("error")
        raise
    if problems:
        for problem in problems:
            logger.error(problem)
        alert_slack(problems)
        sentry_checkin("error")
    else:
        logger.info(f"All {len(PROTECTED_BUCKETS)} buckets have fresh recovery "
                    "points in both regions")
        sentry_checkin("ok")
    return {"problems": problems}
