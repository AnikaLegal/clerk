#!/bin/bash

set -o errexit
set -o pipefail

# Whether to encrypt the backup before upload. Encryption is ON by default; pass
# --no-encrypt for environments whose data does not need it (e.g. staging, which is
# obfuscated).
encrypt_backup=true
while [ $# -gt 0 ]; do
    case "$1" in
        --no-encrypt)
            encrypt_backup=false
            ;;
        *)
            echo -e "\n>>> Error: unknown argument '$1' (supported: --no-encrypt)"
            exit 1
            ;;
    esac
    shift
done

TIME=$(date "+%s")

if [[ -z "$CLERK_PRIVATE_SSH_KEY" ]]; then
    echo -e "\n>>> Error: Environment variable CLERK_PRIVATE_SSH_KEY is required"
    exit 1
fi
if [[ -z "$COMPOSE_SUFFIX" ]]; then
    echo -e "\n>>> Error: Environment variable COMPOSE_SUFFIX is required"
    exit 1
fi
if [[ -z "$S3_BUCKET" ]]; then
    echo -e "\n>>> Error: Environment variable S3_BUCKET is required"
    exit 1
fi

CLERK_HOST=$(grep "^CLERK_HOST=" env/${COMPOSE_SUFFIX}.env | cut -d '=' -f2-)
if [[ -z "$CLERK_HOST" ]]; then
    echo -e "\n>>> Error: CLERK_HOST not found in env/${COMPOSE_SUFFIX}.env"
    exit 1
fi

# Encrypt backups before upload, so the bucket only ever holds ciphertext. 
if [[ "$encrypt_backup" == "true" ]]; then
    if [[ -z "$BACKUP_PASSPHRASE" ]]; then
        echo -e "\n>>> Error: Environment variable BACKUP_PASSPHRASE is required (or pass --no-encrypt)"
        exit 1
    fi
    encrypt=(gpg --batch --quiet --no-symkey-cache --pinentry-mode=loopback \
        --passphrase "$BACKUP_PASSPHRASE" --symmetric --cipher-algo AES256 --output -)
    ext=".gpg"
else
    encrypt=(cat)
    ext=""
fi

DB_FILE="postgres_clerk_${COMPOSE_SUFFIX}_${TIME}.sql${ext}"
DB_PATH="$S3_BUCKET/$DB_FILE"

CLIENT_FILE="client_info_${COMPOSE_SUFFIX}_${TIME}.csv${ext}"
CLIENT_PATH="$S3_BUCKET/$CLIENT_FILE"

MANIFEST_FILE="postgres_clerk_${COMPOSE_SUFFIX}_${TIME}.manifest.json"
MANIFEST_PATH="$S3_BUCKET/$MANIFEST_FILE"

echo -e "\n>>> Setting up SSH"
mkdir ~/.ssh
echo -e "$CLERK_PRIVATE_SSH_KEY" >~/.ssh/id_ed25519
chmod 600 ~/.ssh/id_ed25519
cat >> ~/.ssh/config <<END
Host $CLERK_HOST
  StrictHostKeyChecking no
END

echo -e "\n>>> Setting up Docker context"
docker context create remote --docker "host=ssh://root@${CLERK_HOST}"
docker context use remote

# Database backup
echo -e "\n>>> Streaming database backup from host $CLERK_HOST to $DB_PATH"
docker compose --project-name task \
    --file docker/docker-compose.${COMPOSE_SUFFIX}.yml \
    run --pull always --no-deps --rm web pg_dump --format=custom |
    "${encrypt[@]}" |
    aws s3 cp - $DB_PATH

# Disaster recovery
echo -e "\n>>> Streaming client info from host $CLERK_HOST to $CLIENT_PATH"
docker compose --project-name task \
    --file docker/docker-compose.${COMPOSE_SUFFIX}.yml \
    run --pull always --no-deps --rm web python manage.py export_client_info |
    "${encrypt[@]}" |
    aws s3 cp - $CLIENT_PATH

# Row count manifest, used by the restore check workflow to verify that a
# restored copy of the backup is complete. Contains no sensitive data, so it
# is uploaded unencrypted.
MANIFEST_SQL="SELECT json_build_object(
    'dump_file', '$DB_FILE',
    'server_version', current_setting('server_version'),
    'counts', json_build_object(
        'auth_user', (SELECT count(*) FROM auth_user),
        'core_client', (SELECT count(*) FROM core_client),
        'core_issue', (SELECT count(*) FROM core_issue),
        'emails_email', (SELECT count(*) FROM emails_email),
        'wagtailcore_page', (SELECT count(*) FROM wagtailcore_page)
    )
);"
echo -e "\n>>> Streaming row count manifest from host $CLERK_HOST to $MANIFEST_PATH"
docker compose --project-name task \
    --file docker/docker-compose.${COMPOSE_SUFFIX}.yml \
    run --no-deps --rm web psql --tuples-only --no-align --command "$MANIFEST_SQL" |
    aws s3 cp - $MANIFEST_PATH

echo -e "\n>>> Finished backup"
