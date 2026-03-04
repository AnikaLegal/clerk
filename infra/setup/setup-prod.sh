#!/usr/bin/env bash
set -o errexit

prog=$(basename "$0")

if [ -z "$1" ]; then
    echo "Usage: $prog <HOST>"
    exit 1
fi  
HOST=$1

echo -e "\n>>> Setting up production environment on $HOST"

# Run in subshell to avoid polluting the environment of the rest of the script
# with the envars.
(
    echo -e "\n>>> Importing envars"
    export $(grep -v '^#' env/prod.env | xargs)

    echo -e "\n>>> Initialising Postgres for production on $HOST"
    ssh root@$HOST \
        PGDATABASE=$PGDATABASE \
        PGUSER=$PGUSER \
        PGPASSWORD=$PGPASSWORD \
        /srv/infra/postgres/init.sh
)

echo -e "\n>>> Deploying Clerk for production on host $HOST"
trap "{ docker context rm -f remote; }" EXIT
docker context create remote --docker "host=ssh://root@${HOST}"
docker context use remote

ssh root@$HOST mkdir -p /var/log/clerk/prod/web
ssh root@$HOST mkdir -p /var/log/clerk/prod/worker
docker stack deploy --detach=true --prune --compose-file "docker/docker-compose.prod.yml" clerk_prod

exit 0
