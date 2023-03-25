#!/bin/bash
#
# SSH into our Clerk EC2 instance
# Backup the Postgres DB and upload to S3
#
set -e
HOST='13.55.250.149'
TIME=$(date "+%s")
DATABASE_NAME=clerk
S3_BUCKET=s3://anika-database-backups
BACKUP_FILE="postgres_${DATABASE_NAME}_${TIME}.sql.gz"
S3_PATH="$S3_BUCKET/$BACKUP_FILE"

if [[ -z "$CLERK_PRIVATE_SSH_KEY" ]]
then
    echo -e "\n>>> Error: Clerk private key not found in CLERK_PRIVATE_SSH_KEY."
    exit 1
fi

echo -e "\n>>> Backing up Postgres DB on Clerk EC2 instance at $HOST."

echo -e "\n>>> Setting up private key."
echo -e "$CLERK_PRIVATE_SSH_KEY" > private.key
chmod 600 private.key

echo -e "\n>>> SSH into Clerk EC2 instance at $HOST."
ssh -o StrictHostKeyChecking=no -i private.key root@$HOST /bin/bash << EOF
    set -e
    cd /srv/backups

    pg_dump --format=custom | gzip > $BACKUP_FILE
    echo "$TIME Created local database dump: $BACKUP_FILE"

    aws s3 cp $BACKUP_FILE $S3_PATH
    echo "$TIME Copied local database dump to S3: $S3_PATH"
    
    rm $BACKUP_FILE
    echo "$TIME Removed local database dump to prevent clutter"
EOF

echo -e "\n>>> Finished backing up Postgres DB on Clerk EC2 instance at $HOST."