#!/bin/bash
# Take database backups for the clerk database
# To access psql on the server:
# 
#   su - postgres
#	psql
#
HOST=3.106.55.74
S3_BUCKET=s3://anika-database-backups
DATABASE_NAME=clerk
TIME=$(date "+%s")
BACKUP_FILE="postgres_${DATABASE_NAME}_${TIME}.sql.gz"
BACKUP_DIR=/root/backups
BACKUP_LOCAL="$BACKUP_DIR/$BACKUP_FILE"
BACKUP_S3="$S3_BUCKET/$BACKUP_FILE"
ssh root@$HOST /bin/bash << EOF
    set -e
    export PGHOST=localhost
    export PGDATABASE=$DATABASE_NAME

    echo "Setting up AWS CLI for backups."
    mkdir -p $BACKUP_DIR
    pushd $BACKUP_DIR
    if [[ ! -d "env" ]]; then
        echo "Creating virtualenv and installing AWS CLI."
        virtualenv -p python3 env
        . env/bin/activate
        pip3 install awscli
    else
        . env/bin/activate
    fi

    echo "Creating local database dump $BACKUP_LOCAL"
    pg_dump --format=custom | gzip > $BACKUP_LOCAL

    echo "Copying local dump to S3 - $BACKUP_S3"
    aws s3 cp $BACKUP_LOCAL $BACKUP_S3

    echo "Latest S3 backup:"
    aws s3 ls $S3_BUCKET | sort | tail -n 1
EOF
