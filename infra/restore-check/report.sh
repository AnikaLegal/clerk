#!/usr/bin/env bash

# Report the restore check result (TEC-1987) to Slack.
#
# Posts a pass/fail message with the full check summary to a Slack incoming
# webhook, linking to the workflow run. The summary rides in a code block
# because Slack does not render markdown tables. Skipped with a notice if
# the webhook is not configured; a configured webhook that cannot be posted
# to fails the script.
#
# Environment: OUTCOME (PASS|FAIL), SUMMARY_FILE, RUN_URL, SLACK_WEBHOOK_URL.

set -o nounset
set -o pipefail

OUTCOME="${OUTCOME:?must be PASS or FAIL}"
SUMMARY_FILE="${SUMMARY_FILE:-restore-check-summary.md}"
RUN_URL="${RUN_URL:-}"

if [ -z "${SLACK_WEBHOOK_URL:-}" ]; then
    echo ">>> SLACK_WEBHOOK_URL not set, skipping the Slack report"
    exit 0
fi

echo ">>> Posting result to Slack"
if [ "$OUTCOME" == "PASS" ]; then
    TEXT=":white_check_mark: Database restore check passed."
else
    TEXT=":x: Database restore check FAILED - the latest backup may not be restorable. Please investigate."
fi
if [ -n "$RUN_URL" ]; then
    TEXT+=" Details: $RUN_URL"
fi
SUMMARY=$(cat "$SUMMARY_FILE" 2> /dev/null ||
    echo "No summary file was produced; the check may have crashed early.")
TEXT+=$'\n```\n'"$SUMMARY"$'\n```'

if jq -n --arg text "$TEXT" '{text: $text}' |
    curl -sf -X POST -H "Content-Type: application/json" -d @- "$SLACK_WEBHOOK_URL" > /dev/null; then
    echo ">>> Slack message posted"
else
    echo ">>> Error: failed to post the Slack message" >&2
    exit 1
fi
