#!/bin/bash
# Script to delete and reset db.
function run_docker {
   docker-compose -f docker/docker-compose.local.yml run --rm test $@
} 

# Reset db
run_docker ./manage.py reset_db --close-sessions --noinput

# Setup latest data
run_docker ./manage.py migrate
run_docker ./manage.py createsuperuser --username admin --email admin@example.com --noinput
run_docker ./manage.py shell_plus -c "u=User.objects.get(username='admin');u.set_password('12345');u.save()"
