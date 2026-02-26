#!/usr/bin/env bash
set -o errexit

echo -e "\n>>> Installing Postgres"

# Prevent locale warnings during installation
export LC_ALL=C.UTF-8
export DEBIAN_FRONTEND=noninteractive

apt-get install --yes postgresql postgresql-contrib

echo -e "\n>>> Updating Postgres config"
cp /srv/infra/postgres/pg_hba_retool.conf /etc/postgresql/
chmod 644 /etc/postgresql/pg_hba_retool.conf

HBA_FILE=$(sudo -u postgres psql -tAc 'SHOW hba_file;')
if ! grep -q "pg_hba_retool.conf" "$HBA_FILE"; then
    echo -e "\n>>> Adding pg_hba_retool.conf to Postgres config"
    echo -e "\n\ninclude /etc/postgresql/pg_hba_retool.conf" >> $HBA_FILE
else
    echo -e "\n>>> pg_hba_retool.conf already included in Postgres config"
fi

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
    sudo -Hiu postgres psql -tAc "create database $PGDATABASE;"
    sudo -Hiu postgres psql -tAc "grant all privileges on database $PGDATABASE to $PGUSER;"
else
    echo -e "\n>>> Not creating database $PGDATABASE - already exists."
fi

echo -e "\n>>> Finished installing Postgres"