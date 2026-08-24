#!/usr/bin/env python3
"""Verify a rehearsal restore (TEC-2044, checklist step 6).

Run from the workstation after `just rehearsal restore`:

    verify.py <HOST>

Checks, over SSH to the drill host:

1. Row counts: every table in the backup manifest must match the restored
   clerk_prod database exactly. The manifest checked is the one belonging
   to the dump the restore actually loaded (restore-databases.sh records
   it on the host in /root/clerk-restored-prod), so a nightly backup
   landing mid-drill cannot make the comparison drift.
2. The staging app answers through nginx with a real response (which also
   proves the restored staging database serves queries).
3. The Sentry blackhole holds inside the containers: sentry.io must not
   resolve to a real address from the staging web container, or the
   drill's workers leak errors into the real staging Sentry project.
   This is asserted rather than assumed because the path from the host's
   /etc/hosts to a container's resolver depends on Docker's embedded DNS
   configuration.

Prints a results block ready to paste as the Linear issue comment, and
exits non-zero if any check fails. Reads AWS credentials for the backup
bucket from the environment: the same AWS_BACKUP_USER_* variables
restore-databases.sh uses, or any ambient credentials that can read the
bucket.
"""

import json
import os
import re
import shlex
import subprocess
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

S3_BUCKET = "s3://anika-database-backups"
SSH_OPTS = ["-o", "StrictHostKeyChecking=accept-new"]
STAGING_SERVER_NAME = "staging.anikalegal.org.au"


def run(args: list[str], env: dict | None = None) -> str:
    """Run a command, exiting with its stderr on failure - every failure
    here (bad credentials, unreachable host) needs the underlying message,
    not a traceback."""
    result = subprocess.run(args, check=False, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        sys.exit(f"Error: `{' '.join(args[:2])} ...` failed:\n{result.stderr.strip()}")
    return result.stdout


def backup_env() -> dict:
    """Map the restore script's credential variables onto the AWS CLI's,
    when they are set; otherwise use the ambient environment as-is."""
    env = os.environ.copy()
    if env.get("AWS_BACKUP_USER_ACCESS_KEY"):
        if not env.get("AWS_BACKUP_USER_SECRET_ACCESS_KEY"):
            sys.exit(
                "Error: AWS_BACKUP_USER_ACCESS_KEY is set but "
                "AWS_BACKUP_USER_SECRET_ACCESS_KEY is not - export both, "
                "or neither to use ambient credentials"
            )
        env["AWS_ACCESS_KEY_ID"] = env["AWS_BACKUP_USER_ACCESS_KEY"]
        env["AWS_SECRET_ACCESS_KEY"] = env["AWS_BACKUP_USER_SECRET_ACCESS_KEY"]
        env.pop("AWS_SESSION_TOKEN", None)
    return env


def ssh(host: str, command: str) -> str:
    return run(["ssh", *SSH_OPTS, f"root@{host}", command])


def restored_dump(host: str) -> str:
    """The dump restore-databases.sh recorded that it loaded."""
    name = ssh(host, "cat /root/clerk-restored-prod 2> /dev/null || true").strip()
    if not name:
        sys.exit(
            "Error: /root/clerk-restored-prod is missing on the host - "
            "run `just rehearsal restore` first (it needs the current "
            "restore-databases.sh, which records what it restored)"
        )
    return name


def manifest_for(dump_name: str) -> dict:
    """The row count manifest written alongside the restored dump."""
    manifest_name = re.sub(r"\.sql(\.gpg)?$", "", dump_name) + ".manifest.json"
    env = backup_env()
    listing = run(["aws", "s3", "ls", f"{S3_BUCKET}/{manifest_name}"], env=env)
    if manifest_name not in listing:
        sys.exit(
            f"Error: no manifest {manifest_name} in {S3_BUCKET} - the "
            "restored dump may predate the manifest feature, or the "
            "bucket's retention has expired it"
        )
    return json.loads(
        run(["aws", "s3", "cp", f"{S3_BUCKET}/{manifest_name}", "-"], env=env)
    )


def psql(host: str, sql: str) -> str:
    command = (
        "sudo -Hiu postgres psql --dbname clerk_prod "
        f"--tuples-only --no-align --command {shlex.quote(sql)}"
    )
    return ssh(host, command)


def restored_counts(host: str, tables: list[str]) -> dict[str, int | None]:
    """Row counts for each table, None for tables the restore is missing
    (a missing table is the headline failure, not a crash)."""
    existing = set(
        psql(
            host, "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
        ).split()
    )
    counts: dict[str, int | None] = {table: None for table in tables}
    present = [table for table in tables if table in existing]
    if present:
        sql = " UNION ALL ".join(
            f"SELECT '{table}', count(*) FROM \"{table}\"" for table in present
        )
        for line in psql(host, sql).splitlines():
            table, _, count = line.partition("|")
            counts[table] = int(count)
    return counts


def sentry_resolution(host: str) -> str:
    """What sentry.io resolves to inside the staging web container:
    loopback or nothing means the blackhole holds, anything else is a
    leak. 'unresolved' also covers the container not being up, which the
    app check reports separately."""
    command = (
        "docker exec $(docker ps -q --filter name=clerk_staging_web | head -1) "
        "python3 -c \"import socket; print(socket.gethostbyname('sentry.io'))\" "
        "2> /dev/null || echo unresolved"
    )
    return ssh(host, command).strip() or "unresolved"


def staging_app_status(host: str) -> int:
    """The HTTP status nginx returns for the staging site on the host;
    0 when nothing answered at all (curl's failure is caught remotely so
    a dead socket reports rather than crashes)."""
    curl = (
        "status=$(curl -s -o /dev/null -w '%{http_code}' --max-time 30 "
        f"-H 'Host: {STAGING_SERVER_NAME}' http://127.0.0.1/) "
        "|| status=000; echo $status"
    )
    return int(ssh(host, curl).strip() or 0)


def main() -> int:
    if len(sys.argv) != 2:
        sys.exit(__doc__.strip().splitlines()[0] + "\n\nUsage: verify.py <HOST>")
    host = sys.argv[1]

    dump_name = restored_dump(host)
    print(f">>> The host restored {dump_name}")
    manifest = manifest_for(dump_name)
    expected = manifest["counts"]
    print(f">>> Manifest found: {len(expected)} tables to compare")

    actual = restored_counts(host, list(expected))
    mismatches = {
        table: (count, actual[table])
        for table, count in expected.items()
        if actual[table] != count
    }

    print(">>> Checking the staging app answers through nginx")
    status = staging_app_status(host)
    # The staging vhost proxies to the app, so a real response is 2xx/3xx;
    # 404 would mean nginx's default server answered instead, and 0 that
    # nothing was listening - neither proves the app is up.
    app_ok = 200 <= status < 400

    print(">>> Checking the Sentry blackhole holds inside the containers")
    sentry_address = sentry_resolution(host)
    sentry_ok = sentry_address.startswith("127.") or sentry_address == "unresolved"

    now = datetime.now(tz=ZoneInfo("Australia/Melbourne"))
    lines = [
        f"## Rehearsal verification - {now.date().isoformat()}",
        "",
        (
            "- Host rebuilt from scratch and both databases restored"
            f" ({now.isoformat(timespec='minutes')})"
        ),
        f"- Backup tested: `{dump_name}`",
    ]
    if mismatches:
        lines.append(f"- Row counts: **FAIL** - {len(mismatches)} table(s) diverge:")
        for table, (want, got) in mismatches.items():
            got_text = got if got is not None else "table missing from the restore"
            lines.append(f"  - `{table}`: manifest {want}, restored {got_text}")
    else:
        counts = ", ".join(f"`{t}` {n}" for t, n in expected.items())
        lines.append(f"- Row counts: PASS - all match the manifest exactly ({counts})")
    lines.append(
        f"- Staging app: {'PASS' if app_ok else '**FAIL**'} - "
        f"{f'HTTP {status}' if status else 'no response'} via nginx"
    )
    lines.append(
        "- Sentry blackhole: PASS - containers cannot reach Sentry"
        if sentry_ok
        else f"- Sentry blackhole: **FAIL** - sentry.io resolves to "
        f"{sentry_address} in the web container; drill errors will reach "
        f"the real staging Sentry project"
    )

    print("\n" + "\n".join(lines) + "\n")
    if mismatches or not app_ok or not sentry_ok:
        print(
            ">>> VERIFICATION FAILED - investigate before tearing down", file=sys.stderr
        )
        return 1
    print(">>> Verification passed. Paste the block above into the Linear issue.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
