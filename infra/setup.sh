#!/bin/bash
set -e
HOST='3.106.55.74'

echo -e "\n>>> Importing prod envars"
export $(grep -v '^#' env/prod.env | xargs)

echo -e "\n>>> Setting up $HOST"

echo -e "\n>>> Uploading infra files to $HOST"
ssh root@$HOST mkdir -p /srv/
ssh root@$HOST rm -rf /srv/infra/
scp -r infra/ root@$HOST:/srv/infra/

echo -e "\n>>> Updating apt sources on $HOST"
ssh root@$HOST apt-get update -qq

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
