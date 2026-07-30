#!/usr/bin/env bash

# Run the restore check (TEC-1987) on an ephemeral EC2 instance.
#
# Applies the OpenTofu root at infra/tofu/restore-check/run to launch a
# throwaway instance with Postgres installed, runs check.py on it over SSH,
# extracts the summary for reporting, and destroys the instance again. SSH
# goes through an EC2 Instance Connect Endpoint - an IAM-authenticated
# tunnel to the instance's private address - so the instance accepts no
# connections from the internet, and the per-run SSH key never leaves this
# machine. The instance also self-terminates after an hour as a failsafe if
# this script dies, and each run starts by destroying whatever a previous
# run may have left behind. Production data only ever exists on the
# ephemeral instance, inside our AWS account, and is destroyed with it.
#
# Environment:
#   AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY - the restore-check-ci IAM
#       user (defined in infra/tofu/restore-check/foundations), used to
#       manage the ephemeral instance and open the tunnel.
#   EICE_ID / SUBNET_ID / INSTANCE_SG_ID - the standing Instance Connect
#       Endpoint, subnet and instance security group: the outputs of
#       infra/tofu/restore-check/foundations.
#   CHECK_AWS_ACCESS_KEY_ID / CHECK_AWS_SECRET_ACCESS_KEY - the clerk-backup
#       IAM user, passed to the instance to read the backup bucket.
#   BACKUP_PASSPHRASE, S3_BUCKET - passed to the instance for the check.
#   SUMMARY_FILE - where to write the extracted check summary.

set -o errexit
set -o nounset
set -o pipefail

: "${EICE_ID:?}" "${SUBNET_ID:?}" "${INSTANCE_SG_ID:?}"
: "${CHECK_AWS_ACCESS_KEY_ID:?}" "${CHECK_AWS_SECRET_ACCESS_KEY:?}"
: "${BACKUP_PASSPHRASE:?}" "${S3_BUCKET:?}"
SUMMARY_FILE="${SUMMARY_FILE:-restore-check-summary.md}"

export AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION:-ap-southeast-2}"

TOFU=(tofu -chdir="$(dirname "$0")/../tofu/restore-check/run")
TOFU_ARGS=(-input=false -no-color
    -var "subnet_id=$SUBNET_ID"
    -var "instance_security_group_id=$INSTANCE_SG_ID")
KEY_FILE=$(mktemp -u)

cleanup() {
    echo -e "\n>>> Destroying ephemeral resources"
    "${TOFU[@]}" destroy -auto-approve "${TOFU_ARGS[@]}" || true
    rm -f "$KEY_FILE" "$KEY_FILE.pub"
}
trap cleanup EXIT

"${TOFU[@]}" init -input=false -no-color

# The remote state remembers anything a previous failed run left behind,
# even though that runner is long gone.
echo -e "\n>>> Destroying leftovers from any previous run"
"${TOFU[@]}" destroy -auto-approve "${TOFU_ARGS[@]}"

echo -e "\n>>> Launching ephemeral check instance"
"${TOFU[@]}" apply -auto-approve "${TOFU_ARGS[@]}"
INSTANCE_ID=$("${TOFU[@]}" output -raw instance_id)
echo ">>> Instance $INSTANCE_ID running"

# The pushed public key is valid for 60 seconds of authentication window
# per push (established sessions are unaffected), so it is re-sent before
# each connection attempt.
ssh-keygen -q -t ed25519 -N "" -f "$KEY_FILE"
send_key() {
    aws ec2-instance-connect send-ssh-public-key --instance-id "$INSTANCE_ID" \
        --instance-os-user ubuntu --ssh-public-key "file://$KEY_FILE.pub" > /dev/null
}
SSH=(ssh -i "$KEY_FILE" -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new
    -o UserKnownHostsFile=/dev/null -o ConnectTimeout=10 -o BatchMode=yes
    -o ServerAliveInterval=15
    -o ProxyCommand="aws ec2-instance-connect open-tunnel --instance-connect-endpoint-id $EICE_ID --instance-id %h"
    "ubuntu@$INSTANCE_ID")

echo -e "\n>>> Waiting for the instance to finish setting up"
READY=false
for i in $(seq 1 60); do
    if send_key 2> /dev/null && "${SSH[@]}" 'test -f /var/tmp/restore-check-ready' 2> /dev/null; then
        READY=true
        break
    fi
    sleep 10
done
if [ "$READY" != "true" ]; then
    echo "Error: instance did not become ready in time" >&2
    exit 1
fi

echo -e "\n>>> Running the restore check on the instance"
OUTPUT_LOG=$(mktemp)
CHECK_STATUS=0
send_key
{
    # Secrets travel over SSH stdin only: they never appear in user data,
    # command lines, AWS logs or OpenTofu state. The remote bash reads its
    # script byte by byte, so at the exec line python3 inherits both the
    # exported environment and the rest of the stream: the check script.
    printf 'export AWS_ACCESS_KEY_ID=%q\n' "$CHECK_AWS_ACCESS_KEY_ID"
    printf 'export AWS_SECRET_ACCESS_KEY=%q\n' "$CHECK_AWS_SECRET_ACCESS_KEY"
    printf 'export AWS_DEFAULT_REGION=%q\n' "$AWS_DEFAULT_REGION"
    printf 'export BACKUP_PASSPHRASE=%q\n' "$BACKUP_PASSPHRASE"
    printf 'export S3_BUCKET=%q\n' "$S3_BUCKET"
    printf 'export PGHOST=localhost PGPORT=5432 PGUSER=postgres PGPASSWORD=restore-check\n'
    printf 'exec python3 -\n'
    cat "$(dirname "$0")/check.py"
} | "${SSH[@]}" bash -s | tee "$OUTPUT_LOG" || CHECK_STATUS=$?

awk 'found { print } /===RESTORE-CHECK-SUMMARY===/ { found = 1 }' "$OUTPUT_LOG" > "$SUMMARY_FILE"
rm -f "$OUTPUT_LOG"

exit "$CHECK_STATUS"
