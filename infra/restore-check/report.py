#!/usr/bin/env python3
"""Build and post the restore check's Slack report (TEC-1987).

Builds a Block Kit message from the structured results db-check.py emits
and posts it to a Slack incoming webhook. When no results are available
(the check crashed or timed out before producing any), falls back to a
minimal message built from the outcome alone.

Imported by db-lambda.py, which supplies the results it parsed from the
check's log stream; also runnable as a CLI for local testing, reading the
environment: OUTCOME (PASS|FAIL), RESULTS_FILE, SLACK_WEBHOOK_URL, and
optionally RUN_URL (linked in the message footer). Without a webhook the
CLI just prints a notice; a webhook that cannot be posted to exits
non-zero.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime
from typing import NamedTuple
from zoneinfo import ZoneInfo

STATUS_EMOJI = {"PASS": "white_check_mark", "WARN": "warning", "FAIL": "x"}


# --- Block Kit primitives ---------------------------------------------------


def mrkdwn(text: str) -> dict:
    return {"type": "mrkdwn", "text": text}


def raw(text: str) -> dict:
    return {"type": "raw_text", "text": text}


def emoji(name: str) -> dict:
    return {"type": "emoji", "name": name}


def rich(*elements: dict) -> dict:
    return {
        "type": "rich_text",
        "elements": [{"type": "rich_text_section", "elements": list(elements)}],
    }


def text_run(text: str, **style: bool) -> dict:
    run: dict = {"type": "text", "text": text}
    if style:
        run["style"] = style
    return run


def spacer() -> dict:
    # Block Kit has no spacer block; an effectively-empty section renders
    # as a little vertical white space.
    return {"type": "section", "text": mrkdwn(" ")}


# --- Message assembly -------------------------------------------------------


class Summary(NamedTuple):
    icon: str
    notify: str  # notification and screen reader fallback
    status: str  # the mrkdwn status line under the header


def summarise(outcome: str, checks: list[dict], crashed: bool, name: str) -> Summary:
    warned = [check["label"] for check in checks if check["status"] == "WARN"]
    if outcome != "PASS":
        status = (
            "*FAILED* - no results were produced; the check may have crashed or timed out."
            if crashed
            else "*FAILED* - the latest backup may not be restorable. Please investigate."
        )
        return Summary(":x:", f"{name} FAILED - please investigate.", status)
    if warned:
        plural = "s" if len(warned) > 1 else ""
        return Summary(
            ":warning:",
            f"{name} passed with {len(warned)} warning{plural}.",
            f"*Passed with {len(warned)} warning{plural}* - {', '.join(warned)}",
        )
    return Summary(
        ":white_check_mark:",
        f"{name} passed.",
        "*Passed* - all checks passed",
    )


def human_size(n: float) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if n < 1000 or unit == "GB":
            break
        n /= 1000
    size = f"{n:.1f}".removesuffix(".0")
    return f"{size} {unit}"


def metadata_fields(results: dict) -> list[dict]:
    """The Date / Size / file name facts about the backup that was tested."""
    fields = []
    if results.get("dump_time"):
        date = datetime.fromtimestamp(
            results["dump_time"], tz=ZoneInfo("Australia/Melbourne")
        )
        fields.append(mrkdwn(f"*Date*\n{date.isoformat(timespec='seconds')}"))
    if results.get("dump_bytes"):
        size = f"{human_size(results['dump_bytes'])} db"
        if results.get("client_bytes"):
            size += f" - {human_size(results['client_bytes'])} client"
        fields.append(mrkdwn(f"*Size*\n{size}"))
    if results.get("dump_file"):
        fields.append(mrkdwn(f"*Backup file*\n`{results['dump_file']}`"))
    if results.get("client_file"):
        fields.append(mrkdwn(f"*Client file*\n`{results['client_file']}`"))
    return fields


def label_cell(label: str) -> dict:
    # Row count labels like "auth_user rows" get a code span on the name.
    if label.endswith(" rows"):
        return rich(text_run(label.removesuffix(" rows"), code=True), text_run(" rows"))
    return raw(label)


def detail_cell(value: str, note: str) -> dict:
    if not value:
        return raw(note)
    runs = [text_run(value, bold=True)]
    if note:
        runs.append(text_run(f" {note}"))
    return rich(*runs)


def checks_table(checks: list[dict]) -> dict:
    rows = [[raw("Check"), raw("Result"), raw("Detail")]]
    for check in checks:
        rows.append(
            [
                label_cell(check["label"]),
                rich(emoji(STATUS_EMOJI.get(check["status"], "x"))),
                detail_cell(check.get("value", ""), check.get("note", "")),
            ]
        )
    return {
        "type": "table",
        "column_settings": [
            {"align": "left", "is_wrapped": False},
            {"align": "center", "is_wrapped": False},
            {"align": "left", "is_wrapped": True},
        ],
        "rows": rows,
    }


def footer_blocks(run_url: str | None) -> list[dict]:
    if not run_url:
        return []
    return [{"type": "context", "elements": [mrkdwn(f"<{run_url}|Run log>")]}]


def build_payload(
    results: dict | None,
    outcome: str,
    run_url: str | None = None,
    title: str = "Monthly database restore check",
    name: str = "Database restore check",
) -> dict:
    checks = (results or {}).get("checks", [])
    summary = summarise(outcome, checks, crashed=results is None, name=name)

    blocks: list[dict] = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"{summary.icon} {title}",
                "emoji": True,
            },
        },
        {"type": "section", "text": mrkdwn(summary.status)},
    ]
    if fields := metadata_fields(results or {}):
        blocks.append({"type": "section", "fields": fields})
    if checks:
        blocks += [spacer(), checks_table(checks), spacer()]
    blocks += footer_blocks(run_url)

    return {"text": summary.notify, "blocks": blocks}


# --- Entry point ------------------------------------------------------------


def load_results(path: str) -> dict | None:
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def post(webhook: str, payload: dict) -> None:
    request = urllib.request.Request(
        webhook,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30):
            pass
    except urllib.error.HTTPError as error:
        # Slack names the cause in the body - invalid_token for a revoked
        # webhook, invalid_payload for malformed blocks - and the status
        # alone does not. Raised as a new error rather than re-raising so
        # the webhook URL, a secret, cannot reach a log.
        reason = error.read()[:200].decode(errors="replace").strip()
        raise RuntimeError(f"Slack rejected the post: HTTP {error.code} {reason}") from None


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print the payload instead of posting it",
    )
    args = parser.parse_args()

    outcome = os.environ.get("OUTCOME", "")
    if outcome not in ("PASS", "FAIL"):
        parser.error("environment variable OUTCOME must be PASS or FAIL")

    results = load_results(os.environ.get("RESULTS_FILE", "restore-check-results.json"))
    payload = build_payload(
        results,
        results["outcome"] if results else outcome,
        run_url=os.environ.get("RUN_URL"),
    )

    if args.dry_run:
        print(json.dumps(payload, indent=2))
        return 0

    webhook = os.environ.get("SLACK_WEBHOOK_URL", "")
    if not webhook:
        print(">>> SLACK_WEBHOOK_URL not set, skipping the Slack report")
        return 0

    print(">>> Posting result to Slack")
    try:
        post(webhook, payload)
    except (urllib.error.URLError, OSError, RuntimeError) as error:
        print(f">>> Error: failed to post the Slack message: {error}", file=sys.stderr)
        return 1
    print(">>> Slack message posted")
    return 0


if __name__ == "__main__":
    sys.exit(main())
