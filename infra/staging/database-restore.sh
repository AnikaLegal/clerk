#!/bin/bash
set -o errexit
set -o pipefail

if [[ -z "$CLERK_PRIVATE_SSH_KEY" ]]; then
    echo -e "\n>>> Error: Environment variable CLERK_PRIVATE_SSH_KEY is required"
    exit 1
fi

CLERK_HOST=$(grep "^CLERK_HOST=" env/staging.env | cut -d '=' -f2-)
if [[ -z "$CLERK_HOST" ]]; then
    echo -e "\n>>> Error: CLERK_HOST not found in env/staging.env"
    exit 1
fi

echo -e "\n>>> Setting up SSH"
mkdir ~/.ssh
echo -e "$CLERK_PRIVATE_SSH_KEY" >~/.ssh/id_ed25519
chmod 600 ~/.ssh/id_ed25519
cat >> ~/.ssh/config <<END
Host $CLERK_HOST
  StrictHostKeyChecking no
  ServerAliveInterval 60
END

echo -e "\n>>> Setting up Docker context"
docker context create remote --docker "host=ssh://root@${CLERK_HOST}"
docker context use remote

echo -e "\n>>> Downloading clerk:staging Docker image on host $CLERK_HOST"
docker pull anikalaw/clerk:staging

echo -e "\n>>> Resetting clerk-test database on host $CLERK_HOST"
ssh root@$CLERK_HOST /bin/bash <<EOF
  set -o errexit
  set -o pipefail
  psql -c "SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = 'clerk-test';"
  psql -c "DROP DATABASE IF EXISTS \"clerk-test\";"
  sudo -Hiu postgres -- psql -U postgres -c "CREATE DATABASE \"clerk-test\" WITH OWNER = \"clerk\" ENCODING = 'UTF8';"
EOF

echo -e "\n>>> Restoring staging environment on host $CLERK_HOST"
docker compose \
    --project-name task \
    --file docker/docker-compose.staging.yml \
    run --rm web /app/scripts/tasks/staging-restore.sh

echo -e "\n>>> Restore finished"
