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
marker line; run.sh extracts it for reporting.
"""

import json
import os
import re
import subprocess
import sys
import time

S3_BUCKET = os.environ.get("S3_BUCKET", "")
if not S3_BUCKET:
    sys.exit("Error: S3_BUCKET is required, e.g. s3://anika-database-backups")
DB_NAME = "restore_check"

# Sanity floors used when a dump predates the row count manifest feature.
FLOORS = {"auth_user": 100, "core_issue": 1000, "wagtailcore_page": 50}

RESULTS: list[tuple[str, str, str]] = []


def record(check: str, result: str, detail: str = "") -> None:
    RESULTS.append((check, result, detail))
    print(f">>> {check}: {result} {detail}")


def run_out(args: list[str]) -> str:
    return subprocess.run(args, check=True, capture_output=True, text=True).stdout


def decrypt_cmd(name: str) -> list[str]:
    """The command to decrypt stdin, if the file name indicates encryption."""
    if name.endswith(".gpg"):
        return ["gpg", "--decrypt", "--quiet", "--no-symkey-cache",
                "--pinentry-mode=loopback",
                "--passphrase", os.environ["BACKUP_PASSPHRASE"]]
    return ["cat"]


def s3_stream(name: str) -> tuple[subprocess.Popen, subprocess.Popen]:
    """Stream an object out of the bucket, piped through decryption."""
    fetch = subprocess.Popen(["aws", "s3", "cp", f"{S3_BUCKET}/{name}", "-"],
                             stdout=subprocess.PIPE)
    dec = subprocess.Popen(decrypt_cmd(name), stdin=fetch.stdout,
                           stdout=subprocess.PIPE)
    fetch.stdout.close()
    return fetch, dec


def table_count(table: str) -> int | None:
    try:
        return int(run_out(["psql", "-d", DB_NAME, "-tAc",
                            f"SELECT count(*) FROM {table}"]).strip())
    except (subprocess.CalledProcessError, ValueError):
        return None


def main() -> int:
    print(f"\n>>> Locating latest backup in {S3_BUCKET}")
    listing = [line.split()[-1]
               for line in run_out(["aws", "s3", "ls", f"{S3_BUCKET}/"]).splitlines()
               if line.split()]
    dump_names = sorted(name for name in listing
                        if name.startswith("postgres_clerk") and "manifest" not in name)
    if not dump_names:
        sys.exit(f"Error: no database dump found in {S3_BUCKET}")
    dump_name = dump_names[-1]
    manifest_name = re.sub(r"\.sql(\.gpg)?$", "", dump_name) + ".manifest.json"
    client_names = sorted(name for name in listing if name.startswith("client_info"))
    print(f">>> Latest dump: {dump_name}")

    print("\n>>> Checking backup freshness")
    match = re.fullmatch(r"postgres_clerk_[a-z]+_(\d+)\.sql(\.gpg)?", dump_name)
    if match:
        age = int((time.time() - int(match.group(1))) / 3600)
        # The backup is nightly and the scheduled check runs an hour after
        # it, so a healthy latest dump is about an hour old. One missed
        # night is worth flagging; more than two days means backups have
        # stopped.
        if age <= 26:
            record("backup freshness", "PASS", f"latest dump is {age}h old")
        elif age <= 50:
            record("backup freshness", "WARN",
                   f"latest dump is {age}h old; a nightly backup may have been missed")
        else:
            record("backup freshness", "FAIL",
                   f"latest dump is {age}h old; nightly backups appear to have stopped")
    else:
        record("backup freshness", "WARN",
               f"could not parse a timestamp from {dump_name}")

    print(f"\n>>> Restoring {dump_name} into scratch database {DB_NAME}")
    subprocess.run(["dropdb", "--if-exists", DB_NAME], check=True)
    subprocess.run(["createdb", DB_NAME], check=True)
    fetch, dec = s3_stream(dump_name)
    restore = subprocess.run(["pg_restore", "--no-owner", "--no-privileges",
                              f"--dbname={DB_NAME}"],
                             stdin=dec.stdout, stderr=subprocess.PIPE, text=True)
    dec.stdout.close()
    errors = [line for line in restore.stderr.splitlines()
              if line.startswith("pg_restore:")]
    if not any([restore.returncode, dec.wait(), fetch.wait()]) and not errors:
        record("pg_restore", "PASS", "restored with no errors")
    else:
        example = f", e.g. {errors[0][:150]}" if errors else ""
        record("pg_restore", "FAIL", f"{len(errors)} error lines{example}")

    print("\n>>> Verifying row counts")
    try:
        counts = json.loads(run_out(["aws", "s3", "cp",
                                     f"{S3_BUCKET}/{manifest_name}", "-"]))["counts"]
    except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError):
        counts = None
    if counts:
        for table, expected in counts.items():
            actual = table_count(table)
            # Tolerate small drift: the manifest is written shortly after
            # the dump and some tables (e.g. inbound emails) change around
            # the clock.
            ok = actual is not None and abs(actual - expected) <= max(5, expected / 100)
            record(f"rows: {table}", "PASS" if ok else "FAIL",
                   f"{'n/a' if actual is None else actual} restored vs {expected} at dump time")
    else:
        # Dumps taken before the manifest feature have no manifest; fall
        # back to sanity floors so the check still means something.
        record("manifest", "WARN", f"{manifest_name} not found; using minimum count floors")
        for table, floor in FLOORS.items():
            actual = table_count(table)
            ok = actual is not None and actual >= floor
            record(f"rows: {table}", "PASS" if ok else "FAIL",
                   f"{'n/a' if actual is None else actual} restored (floor {floor})")

    print("\n>>> Verifying client info CSV")
    if client_names:
        client_name = client_names[-1]
        fetch, dec = s3_stream(client_name)
        # Validate without writing the (PII-bearing) content anywhere.
        lines = sum(1 for _ in dec.stdout)
        if not any([dec.wait(), fetch.wait()]) and lines > 1:
            record("client info CSV", "PASS",
                   f"{client_name} decrypts and parses ({lines} lines)")
        else:
            record("client info CSV", "FAIL", f"{client_name} produced {lines} lines")
    else:
        record("client info CSV", "FAIL", f"no client_info file found in {S3_BUCKET}")

    overall = "FAIL" if any(result == "FAIL" for _, result, _ in RESULTS) else "PASS"
    print("===RESTORE-CHECK-SUMMARY===")
    print(f"**Database restore check: {overall}**\n")
    print(f"Backup: `{dump_name}`\n")
    print("| Check | Result | Detail |")
    print("| --- | --- | --- |")
    for check, result, detail in RESULTS:
        print(f"| {check} | {result} | {detail} |")
    return 0 if overall == "PASS" else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    finally:
        subprocess.run(["dropdb", "--if-exists", DB_NAME],
                       check=False, capture_output=True)
