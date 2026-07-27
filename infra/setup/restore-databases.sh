#!/usr/bin/env bash

# Restore the staging and production databases from the latest backups on AWS
# to the specified server, e.g. when migrating to a new server.

set -o errexit
set -o nounset
set -o pipefail

prog=$(basename "$0")
base_dir="$(dirname -- $(dirname -- $(cd -- "$(dirname -- $0)" &> /dev/null && pwd)))"

usage() {
    echo "Usage: $prog <HOST>"
    echo ""
    echo "Restore the staging and production databases from the latest backups"
    echo "on AWS to HOST. The host must already be provisioned (provision.sh)"
    echo "and have its environments initialised (init-env.sh). Refuses to"
    echo "target the current staging or production server."
}

if [ -z "${1:-}" ]; then
    usage
    exit 1
fi
HOST=$1

# Credentials for the clerk-backup IAM user and the backup passphrase can be
# provided via the environment; otherwise they are prompted for. The
# passphrase is kept in the Anika BitWarden (prod backups are GPG-encrypted
# at rest).
if [ -z "${AWS_BACKUP_USER_ACCESS_KEY:-}" ]; then
    read -r -p $'Enter AWS backup user access key id:\n' AWS_BACKUP_USER_ACCESS_KEY
fi
if [ -z "${AWS_BACKUP_USER_SECRET_ACCESS_KEY:-}" ]; then
    read -r -s -p $'Enter AWS backup user secret access key:\n' AWS_BACKUP_USER_SECRET_ACCESS_KEY
fi
if [ -z "${BACKUP_PASSPHRASE:-}" ]; then
    read -r -s -p $'Enter Clerk backup passphrase:\n' BACKUP_PASSPHRASE
fi

export AWS_ACCESS_KEY_ID="$AWS_BACKUP_USER_ACCESS_KEY"
export AWS_SECRET_ACCESS_KEY="$AWS_BACKUP_USER_SECRET_ACCESS_KEY"
# Pass a session token through if one is set, so temporary credentials (e.g.
# from aws login or an assumed role) work too.
if [ -n "${AWS_SESSION_TOKEN:-}" ]; then
    export AWS_SESSION_TOKEN
fi

cd $base_dir

unset LC_ALL
unset LC_CTYPE

# Refuse to run against the current staging or production host, to avoid
# overwriting a live database.
for env_name in staging prod; do
    CURRENT_HOST=$(grep "^CLERK_HOST=" env/${env_name}.env | cut -d '=' -f2-)
    if [ "$HOST" == "$CURRENT_HOST" ]; then
        echo "Error: host $HOST is the current ${env_name} host. Exiting to avoid data loss." >&2
        exit 1
    fi
done

# Automatically accept the host key of a newly provisioned server, but still
# fail on a changed host key.
SSH_OPTS="-o StrictHostKeyChecking=accept-new"

restore_database() {
    local env_name=$1
    local db_name="clerk_${env_name}"

    echo -e "\n>>> Restoring $env_name database from backup to host $HOST"

    # Extract only the variables we need (do not export the whole env file:
    # some values contain spaces, which breaks a bulk export and leaks
    # secret fragments into its error output).
    local pguser pgpassword
    pguser=$(grep '^PGUSER=' env/${env_name}.env | cut -d '=' -f2-)
    pgpassword=$(grep '^PGPASSWORD=' env/${env_name}.env | cut -d '=' -f2-)

    local s3_bucket decrypt
    if [ "$env_name" == "prod" ]; then
        s3_bucket="s3://anika-database-backups"
        # Prod backups are GPG-encrypted at rest.
        decrypt=(gpg --decrypt --quiet --no-symkey-cache
            --pinentry-mode=loopback --passphrase "$BACKUP_PASSPHRASE")
    else
        s3_bucket="s3://anika-database-backups-staging"
        decrypt=(cat)
    fi

    # Locate the backup before touching anything on the host, so that bad
    # credentials or an empty bucket abort with the host left untouched.
    local dump_name
    dump_name=$(aws s3 ls ${s3_bucket} |
        sort |
        grep postgres_clerk |
        tail -n 1 |
        awk '{print $4}')
    echo -e "\n>>> Found backup: $dump_name"

    # Stop the environment's services so nothing writes to the database
    # while it is replaced. Tolerate the services not existing. The scale
    # command can return slightly before the containers have actually
    # exited, so also wait for them to be gone: dropping the database while
    # they are still shutting down races their final queue polls.
    echo -e "\n>>> Stopping $env_name services on $HOST"
    ssh $SSH_OPTS root@$HOST "
        docker service scale ${db_name}_web=0 ${db_name}_worker=0 2> /dev/null || true
        for i in \$(seq 1 30); do
            [ -z \"\$(docker ps -q --filter name=${db_name}_)\" ] && break
            sleep 2
        done"

    # Drop and recreate the database so the restore starts from a clean
    # slate: restoring over an existing schema (e.g. one freshly created by
    # the web container's boot-time migrations) makes pg_restore fail on
    # schema differences. FORCE terminates any remaining connections. The
    # database is recreated by the same init script used by init-env.sh, so
    # ownership and privileges stay consistent.
    echo -e "\n>>> Recreating database $db_name on $HOST"
    ssh $SSH_OPTS root@$HOST \
        "sudo -Hiu postgres psql -tAc 'DROP DATABASE IF EXISTS $db_name WITH (FORCE);'"
    ssh $SSH_OPTS root@$HOST \
        PGDATABASE=$db_name \
        PGUSER=$pguser \
        PGPASSWORD=$pgpassword \
        /srv/infra/postgres/init.sh
    if [ "$env_name" == "staging" ]; then
        # Reapply the staging privilege adjustments made by init-env.sh.
        ssh $SSH_OPTS root@$HOST \
            "sudo -Hiu postgres psql -tAc 'ALTER DATABASE $db_name OWNER TO $pguser;'"
        ssh $SSH_OPTS root@$HOST \
            "sudo -Hiu postgres psql -tAc 'ALTER USER $pguser WITH CREATEDB;'"
    fi

    echo -e "\n>>> Restoring backup $dump_name to host $HOST"
    aws s3 cp ${s3_bucket}/${dump_name} - |
        "${decrypt[@]}" |
        ssh $SSH_OPTS root@$HOST \
        PGDATABASE=$db_name \
        PGUSER=$pguser \
        PGPASSWORD=$pgpassword \
        pg_restore --no-owner --no-privileges --username=$pguser --dbname=$db_name

    echo -e "\n>>> Starting $env_name services on $HOST"
    ssh $SSH_OPTS root@$HOST \
        "docker service scale --detach ${db_name}_web=1 ${db_name}_worker=1 2> /dev/null || true"
}

restore_database staging
restore_database prod

exit 0
