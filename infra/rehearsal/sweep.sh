#!/usr/bin/env bash
# Assert nothing tagged Purpose=rehearsal still exists (TEC-2044,
# checklist teardown step): the throwaway host, its volume and its
# security group must all be gone. Exits non-zero with a listing if
# anything remains. The tagging API keeps deleted resources visible for a
# while, so each ARN is checked against its live state - and only a
# definite "not found" counts as gone: any other API failure (expired
# credentials, throttling) aborts loudly rather than passing a sweep it
# could not actually perform.

set -o errexit
set -o nounset
set -o pipefail

REGION="ap-southeast-2"

errfile=$(mktemp)
trap 'rm -f "$errfile"' EXIT

# probe <ec2 describe args...>: "live", "gone", or abort on anything else.
probe() {
    local out
    if out=$(aws ec2 "$@" --region "$REGION" --output text 2> "$errfile"); then
        # An instance may exist in state "terminated"; anything else that
        # still describes is live.
        if [ "$out" = "terminated" ]; then echo gone; else echo live; fi
    elif grep -q 'NotFound' "$errfile"; then
        echo gone
    else
        echo "Error: could not verify a resource:" >&2
        cat "$errfile" >&2
        exit 2
    fi
}

arns=$(aws resourcegroupstaggingapi get-resources --region "$REGION" \
    --tag-filters Key=Purpose,Values=rehearsal \
    --query 'ResourceTagMappingList[].ResourceARN' --output text)

leftovers=""
for arn in $arns; do
    id="${arn##*/}"
    case "$arn" in
        *:instance/*)
            state=$(probe describe-instances --instance-ids "$id" \
                --query 'Reservations[].Instances[].State.Name')
            ;;
        *:volume/*)
            state=$(probe describe-volumes --volume-ids "$id" \
                --query 'Volumes[].VolumeId')
            ;;
        *:security-group-rule/*)
            state=$(probe describe-security-group-rules --security-group-rule-ids "$id" \
                --query 'SecurityGroupRules[].SecurityGroupRuleId')
            ;;
        *:security-group/*)
            state=$(probe describe-security-groups --group-ids "$id" \
                --query 'SecurityGroups[].GroupId')
            ;;
        *)
            # A resource type this script does not know how to probe:
            # fail safe by listing it for a human to look at.
            state="live"
            ;;
    esac
    if [ "$state" = "live" ]; then
        leftovers="$leftovers  $arn\n"
    fi
done

if [ -n "$leftovers" ]; then
    echo "Error: rehearsal resources still exist:" >&2
    printf '%b' "$leftovers" >&2
    exit 1
fi

echo ">>> Clean: nothing tagged Purpose=rehearsal remains"
exit 0
