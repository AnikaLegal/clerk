#!/usr/bin/env bash

# Migrate the staging and production databases from the latest backup on AWS to
# the specified server.

set -o errexit
prog=$(basename "$0")
base_dir="$(dirname -- $(dirname -- $(cd -- "$(dirname -- $0)" &> /dev/null && pwd)))"

if [ -z "$1" ]; then
    echo "Usage: $prog <HOST>"
    exit 1
fi  
HOST=$1

read -r -s -p $'Enter AWS backup user secret access key:\n' backup_user_secret_access_key
cd $base_dir

unset LC_ALL
unset LC_CTYPE

(
    echo -e "\n>>> Restoring staging database from backup to host $HOST"
    export $(grep -v '^#' env/staging.env | xargs)

    if [ $HOST == $CLERK_HOST ]; then
        echo -e "Error: host $HOST is the same as the current staging host. Exiting to avoid data loss." 2>&1
        exit 0
    fi

    export AWS_ACCESS_KEY_ID="AKIAUZ6OTSVMUXQAJLGM"
    export AWS_SECRET_ACCESS_KEY="$backup_user_secret_access_key"

    S3_BUCKET="s3://anika-database-backups-test"
    DUMP_NAME=$(aws s3 ls ${S3_BUCKET} |
        sort |
        grep postgres_clerk |
        tail -n 1 |
        awk '{{print $4}}')

    echo -e "\n>>> Found backup: $DUMP_NAME"

    echo -e "\n>>> Restoring backup $DUMP_NAME to host $HOST"
    aws s3 cp ${S3_BUCKET}/${DUMP_NAME} - |
        ssh root@$HOST \
        PGDATABASE=clerk_staging \
        PGUSER=$PGUSER \
        PGPASSWORD=$PGPASSWORD \
        pg_restore --clean --no-owner --username=clerk_staging --dbname=clerk_staging
)

(
    echo -e "\n>>> Restoring production database from backup to host $HOST"
    export $(grep -v '^#' env/prod.env | xargs)

    if [ $HOST == $CLERK_HOST ]; then
        echo -e "Error: host $HOST is the same as the current production host. Exiting to avoid data loss." 2>&1
        exit 0
    fi

    export AWS_ACCESS_KEY_ID="AKIAUZ6OTSVMUXQAJLGM"
    export AWS_SECRET_ACCESS_KEY="$backup_user_secret_access_key"

    S3_BUCKET="s3://anika-database-backups"
    DUMP_NAME=$(aws s3 ls ${S3_BUCKET} |
        sort |
        grep postgres_clerk |
        tail -n 1 |
        awk '{{print $4}}')

    echo -e "\n>>> Found backup: $DUMP_NAME"

    echo -e "\n>>> Restoring backup $DUMP_NAME to host $HOST"
    aws s3 cp ${S3_BUCKET}/${DUMP_NAME} - |
        ssh root@$HOST \
        PGDATABASE=clerk_prod \
        PGUSER=$PGUSER \
        PGPASSWORD=$PGPASSWORD \
        pg_restore --clean --no-owner --username=clerk_prod --dbname=clerk_prod
)

exit 0
