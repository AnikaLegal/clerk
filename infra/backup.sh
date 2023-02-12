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
BACKUP_S3="$S3_BUCKET/$BACKUP_FILE"

if [[ -z "$CLERK_PRIVATE_SSH_KEY" ]]
then
    echo -e "\n>>> Error: Clerk private key not found in CLERK_PRIVATE_SSH_KEY."
    exit 1
fi

echo -e "\n>>> Backing up Postgres DB on Clerk EC2 instance at $HOST."

echo -e "\n>>> Setting up private key."
echo -e "$CLERK_PRIVATE_SSH_KEY" > deploy.key
chmod 600 deploy.key

echo -e "\n>>> SSHing into Clerk EC2 instance at $HOST."
ssh -o StrictHostKeyChecking=no -i deploy.key root@$HOST /bin/bash << EOF
    set -e
    cd /srv/backups
    . env/bin/activate
    touch clerk.log

    echo "$TIME Creating local database dump $BACKUP_FILE" >> clerk.log
    pg_dump --format=custom | gzip > $BACKUP_FILE

    echo "$TIME Copying local database dump to S3 - $BACKUP_S3" >> clerk.log
    aws s3 cp $BACKUP_FILE $BACKUP_S3

    BACKUP_RESULT=$(aws s3 ls $S3_BUCKET | sort | grep clerk | tail -n 1)
    echo "$TIME Latest S3 backup: $BACKUP_RESULT" >> clerk.log
    
    rm $BACKUP_FILE
EOF

echo -e "\n>>> Finished backing up Postgres on Clerk EC2 instance at $HOST."