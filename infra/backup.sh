#!/bin/bash

set -o errexit
set -o pipefail

HOST='13.55.250.149'
TIME=$(date "+%s")

if [[ -z "$CLERK_PRIVATE_SSH_KEY" ]]; then
    echo -e "\n>>> Error: Environment variable CLERK_PRIVATE_SSH_KEY is required"
    exit 1
fi
if [[ -z "$COMPOSE_SUFFIX" ]]; then
    echo -e "\n>>> Error: Environment variable COMPOSE_SUFFIX is required"
    exit 1
fi
if [[ -z "$S3_BUCKET" ]]; then
    echo -e "\n>>> Error: Environment variable S3_BUCKET is required"
    exit 1
fi

DB_FILE="postgres_clerk_${COMPOSE_SUFFIX}_${TIME}.sql"
DB_PATH="$S3_BUCKET/$DB_FILE"

echo -e "\n>>> Setting up SSH"
mkdir ~/.ssh
echo -e "$CLERK_PRIVATE_SSH_KEY" >~/.ssh/id_ed25519
chmod 600 ~/.ssh/id_ed25519
cat >> ~/.ssh/config <<END
Host $HOST
  StrictHostKeyChecking no
END

echo -e "\n>>> Setting up Docker context"
docker context create remote --docker "host=ssh://root@${HOST}"
docker context use remote

echo -e "\n>>> Streaming database backup from host $HOST to $DB_PATH"
docker compose --project-name task \
    --file docker/docker-compose.${COMPOSE_SUFFIX}.yml \
    run --no-deps --rm web pg_dump --format=custom |
    aws s3 cp - $DB_PATH

echo -e "\n>>> Finished backup"
