#!/usr/bin/env bash

set -o errexit

echo -e "\nRunning migrations"
./manage.py migrate

export DJANGO_SUPERUSER_PASSWORD=12345
echo -e "\nCreating new superuser 'admin' with password: $DJANGO_SUPERUSER_PASSWORD"
./manage.py createsuperuser \
    --username admin \
    --email admin@example.com \
    --noinput