#!/usr/bin/env bash
set -o errexit

prog=$(basename "$0")

if [ -z "$1" ]; then
    echo "Usage: $prog <HOST>"
    exit 1
fi  
HOST=$1

echo -e "\n>>> Setting up $HOST"
if ssh root@$HOST '[ -d /srv/infra/ ]'; then
    read -p "Looks like host $HOST is already set up. Do you want to continue? (y/N) "
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
fi

echo -e "\n>>> Importing envars"
export $(grep -v '^#' env/prod.env | xargs)

echo -e "\n>>> Copying infra files to $HOST"
ssh root@$HOST mkdir -p /srv/infra
scp -r infra/setup/* root@$HOST:/srv/infra/

echo -e "\n>>> Updating apt sources on $HOST"
ssh root@$HOST apt-get update -qq --yes

echo -e "\n>>> Setting up NGINX on $HOST"
ssh root@$HOST /srv/infra/nginx/setup.sh

echo -e "\n>>> Setting up Postgres on $HOST"
ssh root@$HOST \
    PGDATABASE=$PGDATABASE \
    PGUSER=$PGUSER \
    PGPASSWORD=$PGPASSWORD \
     /srv/infra/postgres/setup.sh

echo -e "\n>>> Setting up Docker on $HOST"
ssh root@$HOST /srv/infra/docker/setup.sh

echo -e "\n>>> Setting up AWS CLI on $HOST"
ssh root@$HOST /srv/infra/aws/setup.sh

echo -e "\n>>> Hardening server on $HOST"
ssh root@$HOST /srv/infra/security/setup.sh

echo -e "\n>>> Finished setting up $HOST"
exit 0
