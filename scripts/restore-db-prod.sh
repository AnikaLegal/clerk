#!/bin/bash
# Script to restore local docker instance db & media from the latest backup on S3
# Requires AWS command line installed & credentials configured with "anika" profile.
function run_docker {
   docker-compose -f docker/docker-compose.local.yml run --rm test $@
} 

# Reset db
run_docker ./manage.py reset_db --close-sessions --noinput

# Download latest backup from S3
S3_BUCKET=s3://anika-database-backups
LATEST_BACKUP=`aws --profile anika s3 ls $S3_BUCKET | sort |  grep postgres_clerk | tail -n 1 | awk '{print $4}'`
aws --profile anika s3 cp ${S3_BUCKET}/${LATEST_BACKUP} - | gunzip | \
    pg_restore \
        --clean \
        --dbname postgres \
        --host localhost \
        --port 25432 \
        --username postgres \
        --no-owner

# Setup latest data
run_docker ./manage.py migrate
run_docker ./manage.py createsuperuser --username admin --email admin@example.com --noinput
run_docker ./manage.py shell_plus -c "u=User.objects.get(username='admin');u.set_password('12345');u.save()"

