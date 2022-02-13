set -e
echo -e "\n>>> Installing Postgres"
apt-get install --yes postgresql postgresql-contrib

echo -e "\n>>> Copying Postgres config"
cp /srv/infra/postgres/pg_hba.conf /etc/postgresql/10/main/pg_hba.conf

echo -e "\n>>> Restarting Postgres"
service postgresql restart

IS_USER_EXISTS=$(sudo -Hiu postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='$PGUSER'")
if [ -z "$IS_USER_EXISTS" ]
then
    echo -e "\n>>> Creating user $PGUSER."
    sudo -Hiu postgres psql -tAc "create user $PGUSER with encrypted password '$PGPASSWORD';"
else
    echo -e "\n>>> Not creating user $PGUSER - already exists."
fi

IS_DB_EXISTS=$(sudo -Hiu postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='$PGDATABASE'")
if [ -z "$IS_DB_EXISTS" ]
then
    echo -e "\n>>> Creating database $PGDATABASE for user $PGUSER."
    sudo -Hiu postgres psql -tAc "create database $PGDATABASE;"
    sudo -Hiu postgres psql -tAc "grant all privileges on database $PGDATABASE to $PGUSER;"
else
    echo -e "\n>>> Not creating database $PGDATABASE - already exists."
fi

echo -e "\n>>> Finished installing Postgres"
