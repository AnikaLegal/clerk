#!/usr/bin/env bash
#
# Break-glass restore of the production database backups from AWS Backup.
#
# Day to day the encrypted Postgres dumps live in the anika-database-backups S3
# bucket and can be pulled with offline-backup.sh. This script is for when that
# bucket itself is gone or unreachable - accidental deletion, corruption, or a
# Sydney region outage: it restores a recovery point (the latest by default) from
# one of the AWS Backup vaults back into a fresh S3 bucket.
#
#   regular      anika-clerk-backup-vault                (Sydney,    ap-southeast-2)
#   airgapped    anika-clerk-logically-air-gapped-vault  (Melbourne, ap-southeast-4)
#
# The air-gapped vault is the last resort: its recovery points are immutable and
# held in a second region, so reach for it if the regular vault is also gone.
#
# The restored objects are the GPG-encrypted dumps. Decrypt the one you need with
# the backup passphrase (Anika BitWarden) - see the hints printed at the end, or
# point restore-databases.sh at the restored bucket.
#
# Credentials come from the environment (e.g. after `aws login`, or an assumed
# admin role). This needs permission to RESTORE - backup:StartRestoreJob,
# iam:PassRole on AWSBackupDefaultServiceRole, and S3 bucket create/write. The
# clerk-backup user is NOT enough; use an admin / break-glass identity.

set -o errexit
set -o nounset
set -o pipefail

prog=$(basename "$0")

RESOURCE_ARN="arn:aws:s3:::anika-database-backups"
RESTORE_ROLE_ARN="arn:aws:iam::330608907609:role/service-role/AWSBackupDefaultServiceRole"

usage() {
    cat <<EOF
Usage: $prog [OPTIONS]

Restore the production database backups from an AWS Backup vault into a new S3
bucket. Defaults to the latest recovery point in the regular (Sydney) vault.

OPTIONS
  -s, --source regular|airgapped   Vault to restore from (default: regular)
  -p, --point latest|<match>       Recovery point: 'latest' (default), a recovery
                                   point ARN, or a date substring to match
                                   (e.g. 2026-07-20).
  -d, --destination <bucket>       Name for the new bucket to restore into
                                   (default: anika-db-restore-<timestamp>).
  -l, --list                       List available recovery points and exit.
      --no-wait                    Start the restore and exit without waiting.
  -h, --help                       Show this help.

Credentials are read from the environment; see the header of this script for the
permissions required.
EOF
}

source=regular
point=latest
destination=""
list_only=false
wait_for_completion=true

while [ $# -gt 0 ]; do
    case "$1" in
        -s|--source) shift; source="${1:-}" ;;
        -p|--point) shift; point="${1:-}" ;;
        -d|--destination) shift; destination="${1:-}" ;;
        -l|--list) list_only=true ;;
        --no-wait) wait_for_completion=false ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Error: unknown argument '$1'" >&2; usage; exit 1 ;;
    esac
    shift
done

case "$source" in
    regular)   vault="anika-clerk-backup-vault"; region="ap-southeast-2" ;;
    airgapped) vault="anika-clerk-logically-air-gapped-vault"; region="ap-southeast-4" ;;
    *) echo "Error: --source must be 'regular' or 'airgapped' (got '$source')" >&2; exit 1 ;;
esac

command -v python3 >/dev/null || { echo "Error: python3 is required" >&2; exit 1; }
aws sts get-caller-identity >/dev/null 2>&1 || {
    echo "Error: not authenticated to AWS. Log in first (e.g. 'aws login')." >&2
    exit 1
}

echo -e "\n>>> Vault: $vault ($region)"

# All recovery points for the database-backups bucket, newest first, one per line
# as: <RecoveryPointArn> <CreationDate> <Status>
recovery_points=$(
    aws backup list-recovery-points-by-backup-vault \
        --backup-vault-name "$vault" --region "$region" \
        --by-resource-arn "$RESOURCE_ARN" \
        --query 'reverse(sort_by(RecoveryPoints,&CreationDate))[].[RecoveryPointArn,CreationDate,Status]' \
        --output text
)
[ -n "$recovery_points" ] || { echo "Error: no recovery points for $RESOURCE_ARN in $vault" >&2; exit 1; }

if [ "$list_only" = true ]; then
    echo -e "\nAvailable recovery points (newest first):\n"
    echo "$recovery_points" | awk '{printf "  %-24s %-10s %s\n", $2, $3, $1}'
    exit 0
fi

# Pick the recovery point: newest for 'latest', otherwise first line matching the
# given ARN or date substring.
if [ "$point" = latest ]; then
    selected=$(echo "$recovery_points" | head -n 1)
else
    selected=$(echo "$recovery_points" | grep -F -- "$point" | head -n 1) || true
fi
[ -n "$selected" ] || { echo "Error: no recovery point matching '$point'. Try --list." >&2; exit 1; }

rp_arn=$(echo "$selected" | awk '{print $1}')
rp_created=$(echo "$selected" | awk '{print $2}')
rp_status=$(echo "$selected" | awk '{print $3}')
echo -e "\n>>> Recovery point: $rp_created ($rp_status)\n    $rp_arn"
[ "$rp_status" = COMPLETED ] || echo "Warning: recovery point status is $rp_status, not COMPLETED." >&2

# Fresh bucket to restore into (created in the vault's region by the restore job).
[ -n "$destination" ] || destination="anika-db-restore-$(date +%Y%m%d-%H%M%S)"
echo -e "\n>>> Restore destination: s3://$destination (new bucket in $region)"

# Build the restore metadata from the recovery point's own template so we don't
# have to hard-code the S3 metadata keys - just override where it lands.
template=$(
    aws backup get-recovery-point-restore-metadata \
        --backup-vault-name "$vault" --region "$region" \
        --recovery-point-arn "$rp_arn" \
        --query 'RestoreMetadata' --output json
)
metadata=$(python3 - "$template" "$destination" <<'PY'
import json, sys
meta = json.loads(sys.argv[1])
# Keep the recovery point's own restore fields (BackupACLs, BackupObjectTags,
# the restore-time window) but drop AWS-internal markers like
# aws:backup:request-id, which start-restore-job does not accept as input.
meta = {k: v for k, v in meta.items() if not k.startswith("aws:")}
meta["DestinationBucketName"] = sys.argv[2]
meta["NewBucket"] = "true"
print(json.dumps(meta))
PY
)

read -r -p $'\nStart this restore? [y/N] ' reply
[ "$reply" = y ] || [ "$reply" = Y ] || { echo "Aborted."; exit 0; }

echo -e "\n>>> Starting restore job"
restore_job_id=$(
    aws backup start-restore-job \
        --region "$region" \
        --recovery-point-arn "$rp_arn" \
        --iam-role-arn "$RESTORE_ROLE_ARN" \
        --resource-type S3 \
        --metadata "$metadata" \
        --query 'RestoreJobId' --output text
)
echo "    restore job: $restore_job_id"

if [ "$wait_for_completion" != true ]; then
    echo -e "\nStarted. Check progress with:"
    echo "  aws backup describe-restore-job --region $region --restore-job-id $restore_job_id"
    exit 0
fi

echo -e "\n>>> Waiting for the restore to complete (this can take a while)..."
while true; do
    status=$(aws backup describe-restore-job --region "$region" \
        --restore-job-id "$restore_job_id" --query 'Status' --output text)
    echo "    status: $status"
    case "$status" in
        COMPLETED) break ;;
        ABORTED|FAILED)
            message=$(aws backup describe-restore-job --region "$region" \
                --restore-job-id "$restore_job_id" --query 'StatusMessage' --output text)
            echo "Error: restore $status - $message" >&2
            exit 1 ;;
    esac
    sleep 30
done

echo -e "\n>>> Restore complete. Dumps are in s3://$destination"
echo "    List:    aws s3 ls s3://$destination/ --region $region"
echo "    Decrypt: aws s3 cp s3://$destination/<file>.sql.gpg - --region $region | \\"
echo "               gpg --decrypt --passphrase <BACKUP_PASSPHRASE> > dump.sql"

exit 0
