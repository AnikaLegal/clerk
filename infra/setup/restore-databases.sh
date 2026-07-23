#!/usr/bin/env bash

# Restore the staging and production databases from the latest backups on AWS
# to the specified server, e.g. when migrating to a new server.

set -o errexit
set -o nounset
set -o pipefail

prog=$(basename "$0")
base_dir="$(dirname -- $(dirname -- $(cd -- "$(dirname -- $0)" &> /dev/null && pwd)))"

usage() {
    echo "Usage: $prog <HOST>"
    echo ""
    echo "Restore the staging and production databases from the latest backups"
    echo "on AWS to HOST. Refuses to target the current staging or production"
    echo "server."
}

if [ -z "${1:-}" ]; then
    usage
    exit 1
fi
HOST=$1

# Credentials for the clerk-backup IAM user and the backup passphrase can be
# provided via the environment; otherwise they are prompted for. The
# passphrase is kept in the Anika BitWarden (prod backups are GPG-encrypted
# at rest).
if [ -z "${AWS_BACKUP_USER_ACCESS_KEY:-}" ]; then
    read -r -p $'Enter AWS backup user access key id:\n' AWS_BACKUP_USER_ACCESS_KEY
fi
if [ -z "${AWS_BACKUP_USER_SECRET_ACCESS_KEY:-}" ]; then
    read -r -s -p $'Enter AWS backup user secret access key:\n' AWS_BACKUP_USER_SECRET_ACCESS_KEY
fi
if [ -z "${BACKUP_PASSPHRASE:-}" ]; then
    read -r -s -p $'Enter Clerk backup passphrase:\n' BACKUP_PASSPHRASE
fi

cd $base_dir

unset LC_ALL
unset LC_CTYPE

# Refuse to run against the current staging or production host, to avoid
# overwriting a live database.
for env_name in staging prod; do
    CURRENT_HOST=$(grep "^CLERK_HOST=" env/${env_name}.env | cut -d '=' -f2-)
    if [ "$HOST" == "$CURRENT_HOST" ]; then
        echo "Error: host $HOST is the current ${env_name} host. Exiting to avoid data loss." >&2
        exit 1
    fi
done

# Automatically accept the host key of a newly provisioned server, but still
# fail on a changed host key.
SSH_OPTS="-o StrictHostKeyChecking=accept-new"

(
    echo -e "\n>>> Restoring staging database from backup to host $HOST"
    # Extract only the variables we need (see init-env.sh for why we do not
    # export the whole env file).
    PGUSER=$(grep '^PGUSER=' env/staging.env | cut -d '=' -f2-)
    PGPASSWORD=$(grep '^PGPASSWORD=' env/staging.env | cut -d '=' -f2-)

    export AWS_ACCESS_KEY_ID="$AWS_BACKUP_USER_ACCESS_KEY"
    export AWS_SECRET_ACCESS_KEY="$AWS_BACKUP_USER_SECRET_ACCESS_KEY"

    S3_BUCKET="s3://anika-database-backups-staging"
    DUMP_NAME=$(aws s3 ls ${S3_BUCKET} |
        sort |
        grep postgres_clerk |
        tail -n 1 |
        awk '{print $4}')

    echo -e "\n>>> Found backup: $DUMP_NAME"

    echo -e "\n>>> Restoring backup $DUMP_NAME to host $HOST"
    aws s3 cp ${S3_BUCKET}/${DUMP_NAME} - |
        ssh $SSH_OPTS root@$HOST \
        PGDATABASE=clerk_staging \
        PGUSER=$PGUSER \
        PGPASSWORD=$PGPASSWORD \
        pg_restore --clean --if-exists --no-owner --no-privileges --username=clerk_staging --dbname=clerk_staging
)

(
    echo -e "\n>>> Restoring production database from backup to host $HOST"
    # Extract only the variables we need (see init-env.sh for why we do not
    # export the whole env file).
    PGUSER=$(grep '^PGUSER=' env/prod.env | cut -d '=' -f2-)
    PGPASSWORD=$(grep '^PGPASSWORD=' env/prod.env | cut -d '=' -f2-)

    export AWS_ACCESS_KEY_ID="$AWS_BACKUP_USER_ACCESS_KEY"
    export AWS_SECRET_ACCESS_KEY="$AWS_BACKUP_USER_SECRET_ACCESS_KEY"

    S3_BUCKET="s3://anika-database-backups"
    DUMP_NAME=$(aws s3 ls ${S3_BUCKET} |
        sort |
        grep postgres_clerk |
        tail -n 1 |
        awk '{print $4}')
    echo -e "\n>>> Found backup: $DUMP_NAME"

    echo -e "\n>>> Restoring backup $DUMP_NAME to host $HOST"
    aws s3 cp ${S3_BUCKET}/${DUMP_NAME} - |
        gpg --decrypt --quiet --no-symkey-cache \
            --pinentry-mode=loopback  --passphrase "$BACKUP_PASSPHRASE" |
        ssh $SSH_OPTS root@$HOST \
        PGDATABASE=clerk_prod \
        PGUSER=$PGUSER \
        PGPASSWORD=$PGPASSWORD \
        pg_restore --clean --if-exists --no-owner --no-privileges --username=clerk_prod --dbname=clerk_prod
)

exit 0
