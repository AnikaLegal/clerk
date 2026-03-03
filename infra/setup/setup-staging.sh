#!/usr/bin/env bash
set -o errexit

prog=$(basename "$0")

if [ -z "$1" ]; then
    echo "Usage: $prog <HOST>"
    exit 1
fi  
HOST=$1

echo -e "\n>>> Setting up staging environment on $HOST"

# Run in subshell to avoid polluting the environment of the rest of the script
# with the envars.
(
    echo -e "\n>>> Importing envars"
    export $(grep -v '^#' env/staging.env | xargs)

    echo -e "\n>>> Initialising Postgres for staging on $HOST"
    ssh root@$HOST \
        PGDATABASE=$PGDATABASE \
        PGUSER=$PGUSER \
        PGPASSWORD=$PGPASSWORD \
        /srv/infra/postgres/init.sh
)

echo -e "\n>>> Deploying Clerk for staging on host $HOST"
docker context create remote --docker "host=ssh://root@${HOST}"
export DOCKER_CONTEXT=remote

ssh root@$HOST mkdir -p /var/log/clerk/staging/web
ssh root@$HOST mkdir -p /var/log/clerk/staging/worker
docker stack deploy --compose-file "docker/docker-compose.staging.yml" clerk_staging
docker context rm -f remote

exit 0
