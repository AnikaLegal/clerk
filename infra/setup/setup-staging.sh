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

    # The following privilege adjustments allow the staging database to be
    # dropped and recreated by PGUSER.

    echo -e "\n>>> Changing ownership of database $PGDATABASE to $PGUSER"
    ssh root@$HOST "sudo -Hiu postgres psql -tAc 'ALTER DATABASE $PGDATABASE OWNER TO $PGUSER;'" 

    echo -e "\n>>> Allow $PGUSER to create databases"
    ssh root@$HOST "sudo -Hiu postgres psql -tAc 'ALTER USER $PGUSER WITH CREATEDB;'"
)

echo -e "\n>>> Deploying Clerk for staging on host $HOST"
trap "{ docker context rm -f remote; }" EXIT
docker context create remote --docker "host=ssh://root@${HOST}"
docker context use remote

ssh root@$HOST mkdir -p /var/log/clerk/staging/web
ssh root@$HOST mkdir -p /var/log/clerk/staging/worker
docker stack deploy --detach=true --prune --compose-file "docker/docker-compose.staging.yml" clerk_staging

exit 0
