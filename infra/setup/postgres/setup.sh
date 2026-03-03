#!/usr/bin/env bash
set -o errexit

echo -e "\n>>> Installing Postgres"
export DEBIAN_FRONTEND=noninteractive

apt-get install --yes postgresql postgresql-contrib

echo -e "\n>>> Updating Postgres config"

HBA_FILE=$(sudo -u postgres psql -tAc 'SHOW hba_file;')
cp /srv/infra/postgres/pg_hba.conf $HBA_FILE
chmod 644 $HBA_FILE

echo -e "\n>>> Restarting Postgres"
systemctl restart postgresql

echo -e "\n>>> Finished installing Postgres"