#!/bin/bash
# Sync prod backups to staging.
echo -e "\nSync AWS S3 assets"
aws s3 sync --acl public-read s3://anika-clerk/images s3://anika-clerk-test/images
aws s3 sync s3://anika-clerk/original_images/ s3://anika-clerk-test/original_images/

echo -e "\nRestoring database from S3 backups"
S3_BUCKET=s3://anika-database-backups
LATEST_BACKUP=`aws s3 ls $S3_BUCKET | sort |  grep postgres_clerk | tail -n 1 | awk '{print $4}'`
aws s3 cp ${S3_BUCKET}/${LATEST_BACKUP} - | gunzip | \
    pg_restore \
        --clean \
        --dbname $PGDATABASE \
        --host $PGHOST \
        --port $PGPORT \
        --username $PGUSER \
        --no-owner

echo -e "\nRunning migrations"
./manage.py migrate

echo -e "\nSetting all Slack messages to send to test alerts channel."
SHELL_CMD="\
space=chr(32);\
c=SlackChannel.objects.get(name=f'Test{space}Alerts');\
SlackMessage.objects.all().update(channel=c);\
SlackUser.objects.all().delete()\
"
./manage.py shell_plus -c "$SHELL_CMD"

echo -e "\nDeleting all Scheduled tasks and Actionstep access tokens."
SHELL_CMD="\
Schedule.objects.all().delete();\
AccessToken.objects.all().delete()\
"
./manage.py shell_plus -c "$SHELL_CMD"

echo -e "\nObsfucating all personally identifiable information."
 ./manage.py obsfucate_actionstep_data

echo -e "\nDatabase restore finished."
