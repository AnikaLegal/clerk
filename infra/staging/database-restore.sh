#!/bin/bash
set -o errexit
set -o pipefail

HOST='13.55.250.149'

if [[ -z "$CLERK_PRIVATE_SSH_KEY" ]]; then
    echo -e "\n>>> Error: Clerk private key not found in CLERK_PRIVATE_SSH_KEY"
    exit 1
fi

echo -e "\n>>> Setting up SSH"
mkdir ~/.ssh
echo -e "$CLERK_PRIVATE_SSH_KEY" >~/.ssh/id_ed25519
chmod 600 ~/.ssh/id_ed25519
cat >> ~/.ssh/config <<END
Host $HOST
  StrictHostKeyChecking no
  ServerAliveInterval 60
END

echo -e "\n>>> Setting up Docker context"
docker context create remote --docker "host=ssh://root@${HOST}"
docker context use remote

echo -e "\n>>> Downloading clerk:staging Docker image on host $HOST"
docker pull anikalaw/clerk:staging

echo -e "\n>>> Resetting clerk-test database on host $HOST"
ssh $HOST /bin/bash <<EOF
  set -o errexit
  set -o pipefail
  psql -c "SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = 'clerk-test';"
  psql -c "DROP DATABASE IF EXISTS \"clerk-test\";"
  sudo -Hiu postgres -- psql -U postgres -c "CREATE DATABASE \"clerk-test\" WITH OWNER = \"clerk\" ENCODING = 'UTF8';"
EOF

echo -e "\n>>> Restoring staging environment on host $HOST"
docker compose \
    --project-name task \
    --file docker/docker-compose.staging.yml \
    run --rm web /app/scripts/tasks/staging-restore.sh

echo -e "\n>>> Restore finished"
