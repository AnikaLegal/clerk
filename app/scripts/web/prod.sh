#!/bin/bash
set -e
echo -e "\n>>> Starting clerk web as `whoami`"

echo -e "\n>>> Setting up logging"
# Set up gunicorn logging
mkdir -p /var/log/gunicorn
touch /var/log/gunicorn/access.log
touch /var/log/gunicorn/error.log

# Set up django logging
touch /var/log/django.log

echo -e "\n>>> Running migrations"
./manage.py migrate

echo -e "\n>>> Setting up schedules"
./manage.py setup_actionstep_tasks

echo -e "\n>>> Starting gunicorn"
gunicorn clerk.wsgi:application \
    --name clerk \
    --workers 2 \
    --bind 0.0.0.0:${GUNICORN_PORT} \
    --capture-output \
    --log-level info \
    --error-logfile /var/log/gunicorn/error.log \
    --access-logfile /var/log/gunicorn/access.log
