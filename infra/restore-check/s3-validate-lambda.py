"""Validate one completed S3 restore testing job (TEC-2063).

Runs as the restore-check-s3-validate Lambda, invoked by EventBridge once
per restore testing job that reaches COMPLETED (the documented validation
hook - see docs/restore-check.md). The job restored a recovery point of a
production bucket into a scratch bucket AWS Backup created
(awsbackup-restore-test-*); this Lambda proves the restored content is
real and stamps the verdict onto the job with PutRestoreValidationResult,
where the restore-check-s3 reporter reads it back. A verdict, once
stamped, is immutable - so a crash here deliberately leaves the job
unstamped rather than recording a FAILED that a transient blip (an S3
throttle, a network reset) would make permanent: the async retries get
another chance to stamp the truth, and a job that stays unstamped is
itself a FAIL row in the report, so nothing fails silently.

What it checks, against the live source bucket:

1. Completeness: every live object last modified before the recovery
   point was taken must exist in the restore. Objects written after the
   snapshot, or deleted since (present in the restore, absent live), are
   expected drift and only counted.
2. Integrity: for objects present in both and unchanged since the
   snapshot, sizes must match; etags too when both are plain MD5s
   (multipart etags vary with part size and are not comparable).
3. Readability: up to 25 objects, sampled evenly across the restored
   listing, are fetched end to end and length-checked.

Melbourne (air-gapped vault) jobs arrive through the same rule via
cross-region event forwarding; the event's region field says where the
job and its scratch bucket live, and the verdict is stamped there.
"""

import logging

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

SOURCE_REGION = "ap-southeast-2"  # the production buckets all live in Sydney
SAMPLE_COUNT = 25

# Ignore churn this close to the recovery point: backup timing is not
# exact, so an object modified just before the snapshot may or may not
# have made it in.
DRIFT_SLACK_SECONDS = 3600

MESSAGE_LIMIT = 1024  # keep the stamped message well under API limits


def bucket_of(arn: str) -> str:
    return arn.split(":::")[-1]


def list_bucket(s3, bucket: str) -> dict[str, dict]:
    """Every current object: key -> {size, etag, modified (epoch)}."""
    objects = {}
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket):
        for entry in page.get("Contents", []):
            objects[entry["Key"]] = {
                "size": entry["Size"],
                "etag": entry["ETag"].strip('"'),
                "modified": entry["LastModified"].timestamp(),
            }
    return objects


def comparable_etags(a: str, b: str) -> bool:
    """Plain-MD5 etags only: multipart etags ("...-N") depend on part size,
    which a restore is free to change."""
    return "-" not in a and "-" not in b


def sample_keys(keys: list[str], count: int) -> list[str]:
    """Up to `count` keys, spread evenly across the sorted listing -
    deterministic, so a re-run reproduces the same sample."""
    keys = sorted(keys)
    if len(keys) <= count:
        return keys
    return [keys[i * len(keys) // count] for i in range(count)]


def validate(job: dict, job_region: str) -> tuple[list[str], str]:
    """Compare the restored bucket against the live source; returns
    (problems, summary)."""
    source = bucket_of(job["SourceResourceArn"])
    restored = bucket_of(job["CreatedResourceArn"])
    snapshot_cutoff = (
        job["RecoveryPointCreationDate"].timestamp() - DRIFT_SLACK_SECONDS
    )

    live_objects = list_bucket(boto3.client("s3", region_name=SOURCE_REGION), source)
    scratch_s3 = boto3.client("s3", region_name=job_region)
    restored_objects = list_bucket(scratch_s3, restored)

    problems = []

    # A restore that produced nothing proves nothing: refuse the vacuous
    # pass whenever the live bucket is not itself empty.
    if not restored_objects and live_objects:
        problems.append(
            f"the restore produced zero objects while the live bucket "
            f"holds {len(live_objects)}"
        )

    # Completeness: anything live that predates the snapshot must be there.
    missing = [
        key
        for key, live in live_objects.items()
        if key not in restored_objects and live["modified"] < snapshot_cutoff
    ]
    if missing:
        problems.append(
            f"{len(missing)} object(s) older than the recovery point are "
            f"missing from the restore, e.g. {missing[0]!r}"
        )

    # Integrity: unchanged-since-snapshot objects must match.
    mismatched = []
    compared = 0
    for key, live in live_objects.items():
        restored_object = restored_objects.get(key)
        if restored_object is None or live["modified"] >= snapshot_cutoff:
            continue
        compared += 1
        if live["size"] != restored_object["size"]:
            mismatched.append(f"{key!r} size {restored_object['size']} != {live['size']}")
        elif live["etag"] != restored_object["etag"] and comparable_etags(
            live["etag"], restored_object["etag"]
        ):
            mismatched.append(f"{key!r} etag mismatch")
    if mismatched:
        problems.append(
            f"{len(mismatched)} restored object(s) do not match the live "
            f"bucket, e.g. {mismatched[0]}"
        )

    # Readability: fetch a sample end to end.
    unreadable = []
    sampled = sample_keys(list(restored_objects), SAMPLE_COUNT)
    for key in sampled:
        try:
            response = scratch_s3.get_object(Bucket=restored, Key=key)
            # Stream rather than buffer: the database dumps run to hundreds
            # of MB, more than this Lambda's memory should ever hold.
            received = sum(
                len(chunk) for chunk in response["Body"].iter_chunks(1024 * 1024)
            )
            if received != response["ContentLength"]:
                unreadable.append(f"{key!r} truncated read")
        except Exception as error:
            unreadable.append(f"{key!r}: {error}")
    if unreadable:
        problems.append(
            f"{len(unreadable)} sampled object(s) could not be read back, "
            f"e.g. {unreadable[0]}"
        )

    drifted = (
        sum(1 for key in live_objects if key not in restored_objects)
        + sum(1 for key in restored_objects if key not in live_objects)
        - len(missing)
    )
    summary = (
        f"{source}: {len(restored_objects)} objects restored; {compared} "
        f"compared against the live bucket, {len(sampled)} fetched, "
        f"{drifted} drifted since the recovery point"
    )
    return problems, summary


def stamp(backup, job_id: str, problems: list[str], summary: str) -> None:
    message = "; ".join(filter(None, [summary] + problems))[:MESSAGE_LIMIT]
    try:
        backup.put_restore_validation_result(
            RestoreJobId=job_id,
            ValidationStatus="FAILED" if problems else "SUCCESSFUL",
            ValidationStatusMessage=message,
        )
    except ClientError as error:
        # EventBridge delivers at least once; a duplicate invocation loses
        # the race to the immutable verdict and that is fine.
        if "already" in str(error).lower():
            logger.warning(f"Verdict for {job_id} was already stamped: {error}")
        else:
            raise


def handler(event, context):
    job_region = event["region"]
    job_id = event["detail"]["restoreJobId"]
    backup = boto3.client("backup", region_name=job_region)
    logger.info(f"Validating restore job {job_id} in {job_region}")

    # No stamp on crash (see the module docstring): raising lets the async
    # retries try again, and an unstamped job still fails the report.
    job = backup.describe_restore_job(RestoreJobId=job_id)
    problems, summary = validate(job, job_region)

    for problem in problems:
        logger.error(problem)
    logger.info(summary)
    stamp(backup, job_id, problems, summary)
    return {"job": job_id, "problems": problems, "summary": summary}
