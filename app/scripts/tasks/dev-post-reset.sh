#!/bin/bash
set -e
echo -e "\nRunning migrations"
./manage.py migrate

echo -e "\nCreating new superuser 'admin'"
./manage.py createsuperuser \
    --username admin \
    --email admin@example.com \
    --noinput


echo -e "\nSetting superuser 'admin' password to 12345"
SHELL_COMMAND="u=User.objects.get(username='admin');u.set_password('12345');u.save();"
./manage.py shell_plus --quiet-load -c "$SHELL_COMMAND"
