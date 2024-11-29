#!/bin/bash
set -e
HOST='13.55.250.149'
PROJECT='staging'
RESTORE_DIR="/srv/restore/clerk_test/$(date +%s)"

if [[ -z "$CLERK_PRIVATE_SSH_KEY" ]]; then
    echo -e "\n>>> Error: Clerk private key not found in CLERK_PRIVATE_SSH_KEY"
    exit 1
fi
echo -e "\n>>> Updating staging environment on Clerk EC2 instance at $HOST"

echo -e "\n>>> Setting up SSH"
mkdir ~/.ssh
echo -e "$CLERK_PRIVATE_SSH_KEY" > ~/.ssh/private.key
chmod 600 ~/.ssh/private.key
cat >> ~/.ssh/config <<END
Host ec2
  HostName $HOST
  User root
  IdentityFile ~/.ssh/private.key
  StrictHostKeyChecking no
  ServerAliveInterval 60
END

echo -e "\n>>> Copying staging compose & env file to clerk at $HOST"
ssh ec2 /bin/bash <<EOF
    set -e
    mkdir -p ${RESTORE_DIR}
EOF
scp docker/docker-compose.staging.yml env/staging.env ec2:$RESTORE_DIR

echo -e "\n>>> SSHing into clerk at $HOST."
ssh ec2 /bin/bash <<EOF
    set -e
    cd ${RESTORE_DIR}
    docker pull anikalaw/clerk:staging
    echo -e "\nResetting database"
    psql -c "SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = 'clerk-test';"
    psql -c "DROP DATABASE IF EXISTS \"clerk-test\";"
    sudo -Hiu postgres -- psql -U postgres -c "CREATE DATABASE \"clerk-test\" WITH OWNER = \"clerk\" ENCODING = 'UTF8';"

    docker compose \
        -p task \
        -f docker-compose.staging.yml \
        run --rm web \
        /app/scripts/tasks/staging-restore.sh
EOF
echo -e "\n>>> Deployment finished for $PROJECT"
