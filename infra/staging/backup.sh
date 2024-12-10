#!/bin/bash
#
# SSH into our Clerk EC2 instance
# Backup the Postgres DB and upload to S3
#
set -e
HOST='13.55.250.149'
TIME=$(date "+%s")
S3_BUCKET='s3://anika-database-backups-test'
BACKUP_FILE="postgres_clerk_staging_${TIME}.sql"
S3_PATH="$S3_BUCKET/$BACKUP_FILE"

if [[ -z "$CLERK_PRIVATE_SSH_KEY" ]]; then
    echo -e "\n>>> Error: Clerk private key not found in CLERK_PRIVATE_SSH_KEY"
    exit 1
fi

echo -e "\n>>> Backing up Postgres DB on Clerk EC2 instance at $HOST"

echo -e "\n>>> Setting up private key"
echo -e "$CLERK_PRIVATE_SSH_KEY" >private.key
chmod 600 private.key

echo -e "\n>>> Streaming backup from Clerk EC2 instance at $HOST"
ssh -T -o StrictHostKeyChecking=no -i private.key root@$HOST \
    'pg_dump --dbname=clerk-test --format=custom' |
    aws s3 cp - $S3_PATH
echo -e "\n>>> Finished backing up Postgres DB on Clerk EC2 instance at $HOST"
