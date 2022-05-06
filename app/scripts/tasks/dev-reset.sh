#!/bin/bash
set -e
echo -e "\nResetting database"
./manage.py reset_db --close-sessions --noinput
. /app/scripts/tasks/dev-post-reset.sh
echo -e "\nDatabase reset finished."
