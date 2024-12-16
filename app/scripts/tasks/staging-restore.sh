#!/bin/bash
# Sync prod backups to staging.

set -o errexit
set -o pipefail

# NOTE: check before blowing the database away!
if [[ $PGDATABASE != "clerk-test" ]]; then
    echo -e "\n>>> Error: unexpected PGDATABASE $PGDATABASE"
    exit 1
fi

echo -e "\nResetting database"
./manage.py reset_db --dbname "$PGDATABASE" --close-sessions --no-input

echo -e "\nRestoring database from backup"
S3_BUCKET="s3://anika-database-backups"
LATEST_BACKUP=$(aws s3 ls $S3_BUCKET |
    sort |
    grep postgres_clerk |
    tail -n 1 |
    awk '{print $4}')
echo -e "\nFound backup $LATEST_BACKUP"

aws s3 cp ${S3_BUCKET}/${LATEST_BACKUP} - |
    pg_restore \
        --clean \
        --dbname $PGDATABASE \
        --host $PGHOST \
        --port $PGPORT \
        --username $PGUSER \
        --no-owner \
        --if-exists

echo -e "\nSync AWS S3 assets"
aws s3 sync --acl public-read s3://anika-clerk/action-documents s3://anika-clerk-test/action-documents
aws s3 sync --acl public-read s3://anika-clerk/documents s3://anika-clerk-test/documents
aws s3 sync --acl public-read s3://anika-clerk/images s3://anika-clerk-test/images
aws s3 sync --acl public-read s3://anika-clerk/original_images s3://anika-clerk-test/original_images
aws s3 sync --acl public-read s3://anika-twilio-audio s3://anika-twilio-audio-test

echo -e "\nRunning migrations"
./manage.py migrate

echo -e "\nSetting all Slack messages to send to test alerts channel"
SHELL_CMD="space=chr(32);\
c=SlackChannel.objects.get(name=f'Test{space}Alerts');\
SlackMessage.objects.all().update(channel=c);\
SlackUser.objects.all().delete()"
./manage.py shell_plus --quiet-load -c "$SHELL_CMD"

echo -e "\nDeleting all Scheduled tasks"
SHELL_CMD="Success.objects.all().delete();\
Failure.objects.all().delete();\
Schedule.objects.all().delete();\
OrmQ.objects.all().delete()"
./manage.py shell_plus --quiet-load -c "$SHELL_CMD"

echo -e "\nObfuscating all personally identifiable information"
./manage.py obfuscate_data

echo -e "\nDatabase restore finished"
