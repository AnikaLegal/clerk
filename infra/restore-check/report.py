#!/usr/bin/env python3
"""Report the restore check result (TEC-1987) to Slack.

Builds a Block Kit message from the structured results check.py emits (which
run.sh extracts into RESULTS_FILE) and posts it to a Slack incoming webhook.
When the results file is missing or unparseable (the check crashed before
producing results), falls back to a minimal message built from OUTCOME
alone. Does nothing but print a notice if no webhook is configured; a
configured webhook that cannot be posted to exits non-zero.

Environment: OUTCOME (PASS|FAIL), SLACK_WEBHOOK_URL, RESULTS_FILE, and
optionally RUN_URL and GITHUB_REPOSITORY (shown in the message footer).
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


def summarise(outcome: str, checks: list[dict], crashed: bool) -> Summary:
    warned = [check["label"] for check in checks if check["status"] == "WARN"]
    if outcome != "PASS":
        status = (
            "*FAILED* - no results were produced; the check may have crashed early."
            if crashed
            else "*FAILED* - the latest backup may not be restorable. Please investigate."
        )
        return Summary(":x:", "Database restore check FAILED - please investigate.", status)
    if warned:
        plural = "s" if len(warned) > 1 else ""
        return Summary(
            ":warning:",
            f"Database restore check passed with {len(warned)} warning{plural}.",
            f"*Passed with {len(warned)} warning{plural}* - {', '.join(warned)}",
        )
    return Summary(
        ":white_check_mark:",
        "Database restore check passed.",
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


def footer_blocks() -> list[dict]:
    parts = []
    if os.environ.get("GITHUB_REPOSITORY"):
        parts.append(os.environ["GITHUB_REPOSITORY"])
    if os.environ.get("RUN_URL"):
        parts.append(f"<{os.environ['RUN_URL']}|Workflow run>")
    if not parts:
        return []
    return [{"type": "context", "elements": [mrkdwn(" - ".join(parts))]}]


def build_payload(results: dict | None, outcome: str) -> dict:
    checks = (results or {}).get("checks", [])
    summary = summarise(outcome, checks, crashed=results is None)

    blocks: list[dict] = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"{summary.icon} Monthly database restore check",
                "emoji": True,
            },
        },
        {"type": "section", "text": mrkdwn(summary.status)},
    ]
    if fields := metadata_fields(results or {}):
        blocks.append({"type": "section", "fields": fields})
    if checks:
        blocks += [spacer(), checks_table(checks), spacer()]
    blocks += footer_blocks()

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
    with urllib.request.urlopen(request, timeout=30):
        pass


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
    payload = build_payload(results, results["outcome"] if results else outcome)

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
    except (urllib.error.URLError, OSError) as error:
        print(f">>> Error: failed to post the Slack message: {error}", file=sys.stderr)
        return 1
    print(">>> Slack message posted")
    return 0


if __name__ == "__main__":
    sys.exit(main())
