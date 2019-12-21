#!/bin/bash
set -e
echo "Starting clerk app as `whoami`"

echo "Starting remote syslog"
mkdir -p /var/log/gunicorn
touch /var/log/gunicorn/access.log
touch /var/log/gunicorn/error.log
remote_syslog \
    --hostname "${PAPERTRAIL_HOSTNAME}" \
    --dest-port "${PAPERTRAIL_PORT}" \
    --dest-host "${PAPERTRAIL_URL}" \
    --pid-file /var/run/remote_syslog.pid \
    /var/log/gunicorn/access.log \
    /var/log/gunicorn/error.log

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
