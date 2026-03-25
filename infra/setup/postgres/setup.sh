#!/usr/bin/env bash
set -o errexit

echo -e "\n>>> Installing Postgres"
export DEBIAN_FRONTEND=noninteractive

apt-get install --yes postgresql postgresql-contrib

echo -e "\n>>> Updating Postgres config"

# Listen on all interfaces for Retool access.
PG_CONF=$(sudo -u postgres psql -tAc 'SHOW config_file;')
sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/g" $PG_CONF

# Use our custom pg_hba.conf to allow access to Retool IPs. See
# https://docs.retool.com/data-sources/guides/connect/postgresql
HBA_FILE=$(sudo -u postgres psql -tAc 'SHOW hba_file;')
cp /srv/infra/postgres/pg_hba.conf $HBA_FILE
chmod 644 $HBA_FILE

echo -e "\n>>> Restarting Postgres"
systemctl restart postgresql

echo -e "\n>>> Finished installing Postgres"