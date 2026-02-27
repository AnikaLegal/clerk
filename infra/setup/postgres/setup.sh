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

echo -e "\n>>> Creating Postgres user and database"

USER_EXISTS=$(sudo -Hiu postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='$PGUSER'")
if [ -z "$USER_EXISTS" ]
then
    echo -e "\n>>> Creating user $PGUSER."
    sudo -Hiu postgres psql -tAc "create user $PGUSER with encrypted password '$PGPASSWORD';"
else
    echo -e "\n>>> Not creating user $PGUSER - already exists."
fi

DB_EXISTS=$(sudo -Hiu postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='$PGDATABASE'")
if [ -z "$DB_EXISTS" ]
then
    echo -e "\n>>> Creating database $PGDATABASE for user $PGUSER."
    sudo -Hiu postgres psql -tAc "CREATE DATABASE \"$PGDATABASE\" WITH OWNER = $PGUSER ENCODING = 'UTF8';"
    sudo -Hiu postgres psql -tAc "grant all privileges on database \"$PGDATABASE\" to $PGUSER;"
else
    echo -e "\n>>> Not creating database $PGDATABASE - already exists."
fi

echo -e "\n>>> Finished installing Postgres"