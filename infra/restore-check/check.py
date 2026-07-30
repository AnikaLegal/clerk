#!/usr/bin/env python3
"""Verify that the latest database backup actually restores (TEC-1987).

Runs on the ephemeral EC2 check instance (see run.sh, which pipes this
script to it over SSH): the dump is restored into a scratch database,
verified, and dropped again. Runnable against any disposable Postgres via
the PG* environment variables.

Requires in the environment: S3_BUCKET, BACKUP_PASSPHRASE (for encrypted
dumps), AWS credentials that can read the backup bucket, and PG* connection
variables for a Postgres server where the connecting role may create and
drop databases.

Prints a markdown summary of the checks after a ===RESTORE-CHECK-SUMMARY===
marker line, then the same results as JSON (plus backup metadata) after a
===RESTORE-CHECK-RESULTS=== marker line; run.sh extracts both for
reporting.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from typing import NamedTuple

S3_BUCKET = os.environ.get("S3_BUCKET", "")
DB_NAME = "restore_check"

# Sanity floors used when a dump predates the row count manifest feature.
FLOORS = {"auth_user": 100, "core_issue": 1000, "wagtailcore_page": 50}


class Backup(NamedTuple):
    """What the bucket listing tells us about the latest backup."""

    dump_name: str
    dump_bytes: int | None
    dump_time: int | None  # unix time parsed from the dump file name
    manifest_name: str
    client_name: str | None
    client_bytes: int | None


class Check(NamedTuple):
    label: str
    status: str  # PASS | WARN | FAIL
    value: str  # the check's headline number, styled by reporting
    note: str


RESULTS: list[Check] = []


def record(label: str, status: str, value: str = "", note: str = "") -> None:
    RESULTS.append(Check(label, status, value, note))
    print(f">>> {label}: {status} {detail(value, note)}")


def detail(value: str, note: str) -> str:
    return " ".join(part for part in (value, note) if part)


# --- S3 and Postgres plumbing ------------------------------------------------


def run_out(args: list[str]) -> str:
    return subprocess.run(args, check=True, capture_output=True, text=True).stdout


def decrypt_cmd(name: str) -> list[str]:
    """The command to decrypt stdin, if the file name indicates encryption."""
    if name.endswith(".gpg"):
        return [
            "gpg", "--decrypt", "--quiet", "--no-symkey-cache",
            "--pinentry-mode=loopback",
            "--passphrase", os.environ["BACKUP_PASSPHRASE"],
        ]
    return ["cat"]


def s3_stream(name: str) -> tuple[subprocess.Popen, subprocess.Popen]:
    """Stream an object out of the bucket, piped through decryption."""
    fetch = subprocess.Popen(
        ["aws", "s3", "cp", f"{S3_BUCKET}/{name}", "-"], stdout=subprocess.PIPE
    )
    dec = subprocess.Popen(
        decrypt_cmd(name), stdin=fetch.stdout, stdout=subprocess.PIPE
    )
    fetch.stdout.close()
    return fetch, dec


def table_count(table: str) -> int | None:
    try:
        return int(
            run_out(
                ["psql", "-d", DB_NAME, "-tAc", f"SELECT count(*) FROM {table}"]
            ).strip()
        )
    except (subprocess.CalledProcessError, ValueError):
        return None


def create_scratch_db() -> None:
    print(f"\n>>> Creating scratch database {DB_NAME}")
    subprocess.run(["dropdb", "--if-exists", DB_NAME], check=True)
    subprocess.run(["createdb", DB_NAME], check=True)


def drop_scratch_db() -> None:
    subprocess.run(["dropdb", "--if-exists", DB_NAME],
                   check=False, capture_output=True)


# --- The checks ---------------------------------------------------------------


def locate_backup() -> Backup:
    print(f"\n>>> Locating latest backup in {S3_BUCKET}")
    listing: dict[str, int] = {}
    for line in run_out(["aws", "s3", "ls", f"{S3_BUCKET}/"]).splitlines():
        parts = line.split()
        if len(parts) == 4 and parts[2].isdigit():
            listing[parts[3]] = int(parts[2])
    dump_names = sorted(
        name for name in listing
        if name.startswith("postgres_clerk") and "manifest" not in name
    )
    if not dump_names:
        sys.exit(f"Error: no database dump found in {S3_BUCKET}")
    dump_name = dump_names[-1]
    print(f">>> Latest dump: {dump_name}")
    match = re.fullmatch(r"postgres_clerk_[a-z]+_(\d+)\.sql(\.gpg)?", dump_name)
    client_names = sorted(name for name in listing if name.startswith("client_info"))
    client_name = client_names[-1] if client_names else None
    return Backup(
        dump_name=dump_name,
        dump_bytes=listing.get(dump_name),
        dump_time=int(match.group(1)) if match else None,
        manifest_name=re.sub(r"\.sql(\.gpg)?$", "", dump_name) + ".manifest.json",
        client_name=client_name,
        client_bytes=listing.get(client_name) if client_name else None,
    )


def check_recency(backup: Backup) -> None:
    print("\n>>> Checking backup freshness")
    if backup.dump_time is None:
        record("Backup recency", "WARN",
               note=f"could not parse a timestamp from {backup.dump_name}")
        return
    age = int((time.time() - backup.dump_time) / 3600)
    # The backup is nightly and the scheduled check runs an hour after it,
    # so a healthy latest dump is about an hour old. One missed night is
    # worth flagging; more than two days means backups have stopped.
    if age <= 26:
        record("Backup recency", "PASS", f"{age}h", "old")
    elif age <= 50:
        record("Backup recency", "WARN", f"{age}h",
               "old; a nightly backup may have been missed")
    else:
        record("Backup recency", "FAIL", f"{age}h",
               "old; nightly backups appear to have stopped")


def check_restore(backup: Backup) -> None:
    print(f"\n>>> Restoring {backup.dump_name} into scratch database {DB_NAME}")
    fetch, dec = s3_stream(backup.dump_name)
    restore = subprocess.run(
        ["pg_restore", "--no-owner", "--no-privileges", f"--dbname={DB_NAME}"],
        stdin=dec.stdout, stderr=subprocess.PIPE, text=True,
    )
    dec.stdout.close()
    errors = [line for line in restore.stderr.splitlines()
              if line.startswith("pg_restore:")]
    if not any([restore.returncode, dec.wait(), fetch.wait()]) and not errors:
        record("Database restore", "PASS", note="no errors")
    else:
        example = f", e.g. {errors[0][:150]}" if errors else ""
        record("Database restore", "FAIL", str(len(errors)), f"error lines{example}")


def check_row_counts(backup: Backup) -> None:
    print("\n>>> Verifying row counts")
    try:
        counts = json.loads(
            run_out(["aws", "s3", "cp", f"{S3_BUCKET}/{backup.manifest_name}", "-"])
        )["counts"]
    except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError):
        counts = None
    if counts:
        for table, expected in counts.items():
            actual = table_count(table)
            # Tolerate small drift: the manifest is written shortly after
            # the dump and some tables (e.g. inbound emails) change around
            # the clock.
            ok = actual is not None and abs(actual - expected) <= max(5, expected / 100)
            record(f"{table} rows", "PASS" if ok else "FAIL",
                   "n/a" if actual is None else f"{actual:,}",
                   f"restored vs {expected:,} at dump time")
    else:
        # Dumps taken before the manifest feature have no manifest; fall
        # back to sanity floors so the check still means something.
        record("Backup manifest", "WARN",
               note="missing; using minimum row floors")
        for table, floor in FLOORS.items():
            actual = table_count(table)
            ok = actual is not None and actual >= floor
            record(f"{table} rows", "PASS" if ok else "FAIL",
                   "n/a" if actual is None else f"{actual:,}",
                   f"restored (floor {floor:,})")


def check_client_csv(backup: Backup) -> None:
    print("\n>>> Verifying client info CSV")
    if not backup.client_name:
        record("Client info", "FAIL",
               note=f"no client_info file found in {S3_BUCKET}")
        return
    fetch, dec = s3_stream(backup.client_name)
    # Validate without writing the (PII-bearing) content anywhere.
    lines = sum(1 for _ in dec.stdout)
    if not any([dec.wait(), fetch.wait()]) and lines > 1:
        record("Client info", "PASS", f"{lines:,}", "lines; decrypts and parses")
    else:
        record("Client info", "FAIL", str(lines), "lines produced")


# --- Output -------------------------------------------------------------------


def print_summary(overall: str, backup: Backup) -> None:
    """The markdown summary, published on the workflow run."""
    print("===RESTORE-CHECK-SUMMARY===")
    print(f"**Database restore check: {overall}**\n")
    print(f"Backup: `{backup.dump_name}`\n")
    print("| Check | Result | Detail |")
    print("| --- | --- | --- |")
    for check in RESULTS:
        print(f"| {check.label} | {check.status} | {detail(check.value, check.note)} |")


def print_results(overall: str, backup: Backup) -> None:
    """The same results as JSON, rendered for Slack by report.py."""
    print("===RESTORE-CHECK-RESULTS===")
    print(json.dumps({
        "outcome": overall,
        "dump_file": backup.dump_name,
        "dump_bytes": backup.dump_bytes,
        "dump_time": backup.dump_time,
        "client_file": backup.client_name,
        "client_bytes": backup.client_bytes,
        "checks": [check._asdict() for check in RESULTS],
    }))


# --- Entry point --------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.parse_args()
    if not S3_BUCKET:
        parser.error(
            "environment variable S3_BUCKET is required, e.g. s3://anika-database-backups"
        )

    backup = locate_backup()
    check_recency(backup)

    # The scratch database is only ever dropped by the process that
    # created it, even when a check crashes partway.
    create_scratch_db()
    try:
        check_restore(backup)
        check_row_counts(backup)
        check_client_csv(backup)
    finally:
        drop_scratch_db()

    overall = "FAIL" if any(check.status == "FAIL" for check in RESULTS) else "PASS"
    print_summary(overall, backup)
    print_results(overall, backup)
    return 0 if overall == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
