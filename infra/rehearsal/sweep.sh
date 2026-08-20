#!/usr/bin/env bash
# Assert nothing tagged Purpose=rehearsal still exists (TEC-2044,
# checklist teardown step): the throwaway host, its volume, its security
# group, its VPC and that VPC's plumbing must all be gone. Exits non-zero with a listing if
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

# probe <service> <command args...>: "live", "gone", or abort on anything
# else. Only definitive answers classify: NotFound/NoSuchHostedZone or an
# irreversible terminal state mean gone. A successful describe with an
# empty answer means the API has not settled around a recent change, so
# it is retried - and still counts as live if it never settles, leaving
# the operator to re-run the sweep rather than trusting an unproven
# clean.
probe() {
    local out attempt
    for attempt in 1 2 3 4 5 6; do
        if out=$(aws "$@" --region "$REGION" --output text 2> "$errfile"); then
            case "$out" in
                "") sleep 5 ;;
                "terminated" | "shutting-down") echo "gone"; return ;;
                *) echo "live"; return ;;
            esac
        elif grep -qE 'NotFound|NoSuchHostedZone' "$errfile"; then
            echo "gone"
            return
        else
            echo "Error: could not verify a resource:" >&2
            cat "$errfile" >&2
            exit 2
        fi
    done
    echo "live"
}

arns=$(aws resourcegroupstaggingapi get-resources --region "$REGION" \
    --tag-filters Key=Purpose,Values=rehearsal \
    --query 'ResourceTagMappingList[].ResourceARN' --output text)

leftovers=""
for arn in $arns; do
    id="${arn##*/}"
    case "$arn" in
        *:instance/*)
            state=$(probe ec2 describe-instances --instance-ids "$id" \
                --query 'Reservations[].Instances[].State.Name')
            ;;
        *:volume/*)
            state=$(probe ec2 describe-volumes --volume-ids "$id" \
                --query 'Volumes[].VolumeId')
            ;;
        *:security-group-rule/*)
            state=$(probe ec2 describe-security-group-rules --security-group-rule-ids "$id" \
                --query 'SecurityGroupRules[].SecurityGroupRuleId')
            ;;
        *:security-group/*)
            state=$(probe ec2 describe-security-groups --group-ids "$id" \
                --query 'SecurityGroups[].GroupId')
            ;;
        *:hostedzone/*)
            state=$(probe route53 get-hosted-zone --id "$id" \
                --query 'HostedZone.Id')
            ;;
        *:vpc/*)
            state=$(probe ec2 describe-vpcs --vpc-ids "$id" \
                --query 'Vpcs[].VpcId')
            ;;
        *:subnet/*)
            state=$(probe ec2 describe-subnets --subnet-ids "$id" \
                --query 'Subnets[].SubnetId')
            ;;
        *:internet-gateway/*)
            state=$(probe ec2 describe-internet-gateways --internet-gateway-ids "$id" \
                --query 'InternetGateways[].InternetGatewayId')
            ;;
        *:route-table/*)
            state=$(probe ec2 describe-route-tables --route-table-ids "$id" \
                --query 'RouteTables[].RouteTableId')
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
