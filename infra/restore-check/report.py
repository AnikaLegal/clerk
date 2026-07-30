#!/usr/bin/env python3
"""Report the restore check result (TEC-1987) to Slack.

Builds a Block Kit message from the structured results check.py emits (which
run.sh extracts into RESULTS_FILE) and posts it to a Slack incoming webhook.
When the results file is missing or unparseable (the check crashed before
producing results), falls back to a minimal message built from OUTCOME
alone. Does nothing but print a notice if no webhook is configured; a
configured webhook that cannot be posted to exits non-zero.

Pass --dry-run to print the payload instead of posting it.

Environment: OUTCOME (PASS|FAIL), SLACK_WEBHOOK_URL, RESULTS_FILE, and
optionally RUN_URL and GITHUB_REPOSITORY (shown in the message footer).
"""

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

EMOJI = {"PASS": "white_check_mark", "WARN": "warning", "FAIL": "x"}


def human_size(n: float) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if n < 1000 or unit == "GB":
            break
        n /= 1000
    size = f"{n:.1f}".removesuffix(".0")
    return f"{size} {unit}"


def mrkdwn(text: str) -> dict:
    return {"type": "mrkdwn", "text": text}


def raw(text: str) -> dict:
    return {"type": "raw_text", "text": text}


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


def build_payload(results: dict | None, outcome: str) -> dict:
    checks = (results or {}).get("checks", [])
    warnings = sum(1 for check in checks if check["status"] == "WARN")

    if outcome != "PASS":
        icon = ":x:"
        notify = "Database restore check FAILED - please investigate."
        status = (
            "*FAILED* - the latest backup may not be restorable. Please investigate."
        )
        if not results:
            status = (
                "*FAILED* - no results were produced; the check may have crashed early."
            )
    elif warnings:
        icon = ":warning:"
        plural = "s" if warnings > 1 else ""
        warned = ", ".join(c["label"] for c in checks if c["status"] == "WARN")
        notify = f"Database restore check passed with {warnings} warning{plural}."
        status = f"*Passed with {warnings} warning{plural}* - {warned}"
    else:
        icon = ":white_check_mark:"
        notify = "Database restore check passed."
        status = "*Passed* - all checks passed"

    blocks: list[dict] = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"{icon} Monthly database restore check",
                "emoji": True,
            },
        },
        {"type": "section", "text": mrkdwn(status)},
    ]

    fields = []
    if results:
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
    if fields:
        blocks.append({"type": "section", "fields": fields})

    if checks:
        rows = [[raw("Check"), raw("Result"), raw("Detail")]]
        for check in checks:
            rows.append(
                [
                    label_cell(check["label"]),
                    rich({"type": "emoji", "name": EMOJI.get(check["status"], "x")}),
                    detail_cell(check.get("value", ""), check.get("note", "")),
                ]
            )
        blocks.append(
            {
                "type": "table",
                "column_settings": [
                    {"align": "left", "is_wrapped": False},
                    {"align": "center", "is_wrapped": False},
                    {"align": "left", "is_wrapped": True},
                ],
                "rows": rows,
            }
        )

    footer = []
    if os.environ.get("GITHUB_REPOSITORY"):
        footer.append(os.environ["GITHUB_REPOSITORY"])
    if os.environ.get("RUN_URL"):
        footer.append(f"<{os.environ['RUN_URL']}|Workflow run>")
    if footer:
        blocks.append({"type": "divider"})
        blocks.append({"type": "context", "elements": [mrkdwn(" - ".join(footer))]})

    # The top-level text is the notification and screen reader fallback.
    return {"text": notify, "blocks": blocks}


def main() -> int:
    outcome = os.environ.get("OUTCOME", "")
    if outcome not in ("PASS", "FAIL"):
        sys.exit("Error: OUTCOME must be PASS or FAIL")
    dry_run = "--dry-run" in sys.argv[1:]

    results_file = os.environ.get("RESULTS_FILE", "restore-check-results.json")
    try:
        with open(results_file) as f:
            results = json.load(f)
    except (OSError, json.JSONDecodeError):
        results = None

    payload = build_payload(results, results["outcome"] if results else outcome)

    if dry_run:
        print(json.dumps(payload, indent=2))
        return 0

    webhook = os.environ.get("SLACK_WEBHOOK_URL", "")
    if not webhook:
        print(">>> SLACK_WEBHOOK_URL not set, skipping the Slack report")
        return 0

    print(">>> Posting result to Slack")
    request = urllib.request.Request(
        webhook,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30):
            pass
    except (urllib.error.URLError, OSError) as error:
        print(f">>> Error: failed to post the Slack message: {error}", file=sys.stderr)
        return 1
    print(">>> Slack message posted")
    return 0


if __name__ == "__main__":
    sys.exit(main())
