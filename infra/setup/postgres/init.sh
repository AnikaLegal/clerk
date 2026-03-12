#!/usr/bin/env bash
set -o errexit

echo -e "\n>>> Initialising Postgres"

USER_EXISTS=$(sudo -Hiu postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='$PGUSER'")
if [ -z "$USER_EXISTS" ]
then
    echo -e "\n>>> Creating user $PGUSER."
    sudo -Hiu postgres psql -tAc "CREATE USER $PGUSER WITH ENCRYPTED PASSWORD '$PGPASSWORD';"
else
    echo -e "\n>>> Not creating user $PGUSER - already exists."
fi

DB_EXISTS=$(sudo -Hiu postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='$PGDATABASE'")
if [ -z "$DB_EXISTS" ]
then
    echo -e "\n>>> Creating database $PGDATABASE for user $PGUSER."
    sudo -Hiu postgres psql -tAc "CREATE DATABASE $PGDATABASE WITH OWNER = postgres ENCODING = 'UTF8';"
    sudo -Hiu postgres psql -tAc "GRANT ALL PRIVILEGES ON DATABASE $PGDATABASE TO $PGUSER;"
    sudo -Hiu postgres psql -d $PGDATABASE -tAc "GRANT CREATE ON SCHEMA public TO $PGUSER;"
else
    echo -e "\n>>> Not creating database $PGDATABASE - already exists."
fi

echo -e "\n>>> Finished initialising Postgres"