#!/bin/bash
set -e
export PGHOST=clerk_db
export PGPORT=5432
export PGDATABASE=postgres
export PGUSER=postgres
export PGPASSWORD=password
BACKUP_BUCKET_NAME="anika-database-backups"
S3_BUCKET="s3://${BACKUP_BUCKET_NAME}"

echo -e "\nRestoring database from production backups."
./manage.py reset_db --close-sessions --noinput

echo -e "\nRestoring database from S3 backups at ${S3_BUCKET}"
DUMP_NAME=$( \
    aws s3 ls ${S3_BUCKET} | \
    sort | grep postgres_clerk | \
    tail -n 1 | \
    awk '{{print $4}}'
)
echo -e "\nFound dump $DUMP_NAME"
! aws s3 cp ${S3_BUCKET}/${DUMP_NAME} - | gunzip | pg_restore -d $PGDATABASE --no-owner

. /app/scripts/tasks/dev-post-reset.sh

echo -e "\nSetting all Slack messages to send to test alerts channel."
SHELL_CMD="space=chr(32);\
c=SlackChannel.objects.get(name=f'Test{space}Alerts');\
SlackMessage.objects.all().update(channel=c);\
SlackUser.objects.all().delete()"
./manage.py shell_plus --quiet-load -c "${SHELL_CMD}"

echo -e "\nDeleting all Scheduled tasks."
SHELL_CMD="Success.objects.all().delete();\
Failure.objects.all().delete();\
Schedule.objects.all().delete();\
OrmQ.objects.all().delete();\
./manage.py shell_plus --quiet-load -c "${SHELL_CMD}"

echo -e "\nDatabase restore finished."
