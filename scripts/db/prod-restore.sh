#!/bin/bash
# Script to restore local docker instance DB from the latest backup on S3
# Requires AWS command line installed & credentials configured with "anika" profile.
function run_docker {
   docker-compose -f docker/docker-compose.local.yml run --rm test $@
} 

# Reset db
echo -e "\nResetting database"
run_docker ./manage.py reset_db --close-sessions --noinput

# Download latest backup from S3
echo -e "\nRestoring database from S3 backups"
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
echo -e "\nRunning migrations"
run_docker ./manage.py migrate

echo -e "\nCreating new superuser 'admin'"
run_docker ./manage.py createsuperuser \
   --username admin \
   --email admin@example.com \
   --noinput

echo -e "\nSetting superuser 'admin' password to 12345"
SHELL_CMD="\
Group.objects.get_or_create(name='Impact');\
u=User.objects.get(username='admin');\
u.set_password('12345');\
u.first_name='Admin';\
u.last_name='Example';\
u.save();\
"
run_docker ./manage.py shell_plus -c "$SHELL_CMD"

echo -e "\nSetting all Slack messages to send to test alerts channel."
SHELL_CMD="\
space=chr(32);\
c=SlackChannel.objects.get(name=f'Test{space}Alerts');\
SlackMessage.objects.all().update(channel=c);\
SlackUser.objects.all().delete()\
"
run_docker ./manage.py shell_plus -c "$SHELL_CMD"

echo -e "\nDeleting all Scheduled tasks and Actionstep access tokens."
SHELL_CMD="\
Success.objects.all().delete();\
Failure.objects.all().delete();\
Schedule.objects.all().delete();\
OrmQ.objects.all().delete();\
AccessToken.objects.all().delete()\
"
run_docker ./manage.py shell_plus -c "$SHELL_CMD"

echo -e "\nDatabase restore finished."
