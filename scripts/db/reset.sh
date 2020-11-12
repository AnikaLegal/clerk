#!/bin/bash
# Script to delete and reset db.
function run_docker {
   docker-compose -f docker/docker-compose.local.yml run --rm test $@
} 

# Stop all Docker containers
echo -e "\nStopping all running Docker containers"
docker update --restart=no `docker ps -q`
docker kill `docker ps -q`

# Reset db
echo -e "\nResetting database"
run_docker ./manage.py reset_db --close-sessions --noinput

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
u.save();\
"
run_docker ./manage.py shell_plus -c "$SHELL_CMD"
echo -e "\nDatabase reset finished."
