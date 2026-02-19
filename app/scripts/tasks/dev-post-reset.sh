#!/usr/bin/env bash

set -o errexit

echo -e "\nRunning migrations"
./manage.py migrate

export DJANGO_SUPERUSER_PASSWORD="admin"
echo -e "\nCreating new superuser 'admin' with password: $DJANGO_SUPERUSER_PASSWORD"
./manage.py createsuperuser \
    --username admin \
    --email admin@example.com \
    --noinput

SHELL_CMD="space=chr(32);\
u=User.objects.get(username='admin');\
u.first_name='Admin';\
u.last_name='User';\
u.save()"
./manage.py shell_plus --quiet-load -c "${SHELL_CMD}"