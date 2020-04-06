#!/bin/bash
set -e
echo "Starting clerk web as `whoami`"

echo "Setting up logging"
# Set up gunicorn logging
mkdir -p /var/log/gunicorn
touch /var/log/gunicorn/access.log
touch /var/log/gunicorn/error.log

# Set up django logging
touch /var/log/django.log

echo "Running migrations"
./manage.py migrate

echo "Starting gunicorn"
gunicorn clerk.wsgi:application \
    --name clerk \
    --workers 2 \
    --bind 0.0.0.0:${GUNICORN_PORT} \
    --capture-output \
    --log-level info \
    --error-logfile /var/log/gunicorn/error.log \
    --access-logfile /var/log/gunicorn/access.log
