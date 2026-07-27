#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

prog=$(basename "$0")
base_dir="$(dirname -- $(dirname -- $(cd -- "$(dirname -- $0)" &> /dev/null && pwd)))"

usage() {
    echo "Usage: $prog <HOST> <staging|prod>"
    echo ""
    echo "Initialise a Clerk environment on a provisioned host: create the"
    echo "Postgres user and database, create the log directories and deploy"
    echo "the Docker Swarm stack."
}

if [ -z "${1:-}" ] || [ -z "${2:-}" ]; then
    usage
    exit 1
fi
HOST=$1
ENV_NAME=$2

case "$ENV_NAME" in
    staging|prod) ;;
    *)
        echo "Error: unknown environment '$ENV_NAME' (supported: staging, prod)" >&2
        usage
        exit 1
        ;;
esac

# Automatically accept the host key of a newly provisioned server, but still
# fail on a changed host key. The first ssh call below also seeds known_hosts
# for the docker-over-ssh context.
SSH_OPTS="-o StrictHostKeyChecking=accept-new"

echo -e "\n>>> Setting up $ENV_NAME environment on $HOST"
cd $base_dir

# Run in subshell to avoid polluting the environment of the rest of the script
# with the envars.
(
    echo -e "\n>>> Importing envars"
    # Extract only the variables we need. Do not export the whole env file:
    # some values (e.g. private keys) contain spaces, which breaks a bulk
    # export and leaks secret fragments into its error output.
    PGDATABASE=$(grep '^PGDATABASE=' env/$ENV_NAME.env | cut -d '=' -f2-)
    PGUSER=$(grep '^PGUSER=' env/$ENV_NAME.env | cut -d '=' -f2-)
    PGPASSWORD=$(grep '^PGPASSWORD=' env/$ENV_NAME.env | cut -d '=' -f2-)

    echo -e "\n>>> Initialising Postgres for $ENV_NAME on $HOST"
    ssh $SSH_OPTS root@$HOST \
        PGDATABASE=$PGDATABASE \
        PGUSER=$PGUSER \
        PGPASSWORD=$PGPASSWORD \
        /srv/infra/postgres/init.sh

    if [ "$ENV_NAME" == "staging" ]; then
        # The following privilege adjustments allow the staging database to be
        # dropped and recreated by PGUSER.

        echo -e "\n>>> Changing ownership of database $PGDATABASE to $PGUSER"
        ssh $SSH_OPTS root@$HOST "sudo -Hiu postgres psql -tAc 'ALTER DATABASE $PGDATABASE OWNER TO $PGUSER;'"

        echo -e "\n>>> Allow $PGUSER to create databases"
        ssh $SSH_OPTS root@$HOST "sudo -Hiu postgres psql -tAc 'ALTER USER $PGUSER WITH CREATEDB;'"
    fi
)

echo -e "\n>>> Deploying Clerk for $ENV_NAME on host $HOST"
trap "{ docker context rm -f remote; }" EXIT
# Remove any leftover context from a previous run that was killed before its
# EXIT trap could clean up.
docker context rm -f remote &> /dev/null || true
docker context create remote --docker "host=ssh://root@${HOST}"
docker context use remote

ssh $SSH_OPTS root@$HOST mkdir -p /var/log/clerk/$ENV_NAME/web
ssh $SSH_OPTS root@$HOST mkdir -p /var/log/clerk/$ENV_NAME/worker
docker stack deploy --detach=true --prune --compose-file "docker/docker-compose.$ENV_NAME.yml" clerk_$ENV_NAME

exit 0
