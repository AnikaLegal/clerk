#!/usr/bin/env bash

set -o errexit
set -o pipefail

s3_bucket="s3://anika-database-backups"
prog="$(basename $BASH_SOURCE)"
usage="Usage: ${prog} [OPTIONS]

OPTIONS
  -d, --decrypt <FILE>  Decrypt the supplied offline backup file.
  -h, --help            Show this help.
  
When no options are supplied the latest backup file will be downloaded from AWS
to the current directory and encrypted."

# Pass command line args.
decrypt_file=""
while [ $# -gt 0 ]; do
    case "$1" in
        -d|--decrypt)
            shift
            decrypt_file="$1"
            ;;
        -h|--help)
            echo "$usage"
            exit 0
            ;;
        *)
            echo "$usage" 1>&2
            exit 1
            ;;
    esac
    shift
done

if [ -n "$decrypt_file" ]; then
    # Read required secret. Passphrase in Anika BitWarden.
    read -r -s -p $'Enter Clerk offline backup passphrase:\n' passphrase

    echo "Decrypting backup file $decrypt_file"
    output="${decrypt_file%.data}"
    gpg --no-symkey-cache --output "${output}" --pinentry-mode=loopback \
        --passphrase "${passphrase}" --decrypt "$decrypt_file"
else
    # Read required secret. Key in Anika BitWarden.
    read -r -s -p $'Enter AWS backup user secret access key:\n' AWS_SECRET_ACCESS_KEY
    export AWS_ACCESS_KEY_ID="AKIAUZ6OTSVMUXQAJLGM"
    export AWS_SECRET_ACCESS_KEY

    # Read required secret. Passphrase in Anika BitWarden.
    read -r -s -p $'Enter Clerk offline backup passphrase:\n' passphrase

    # Get the db backup from the AWS prod backup bucket.
    echo "Finding latest database backup..."
    db_backup_file=$(
        aws s3 ls ${s3_bucket} |
            sort |
            grep postgres_clerk |
            tail -n 1 |
            awk '{{print $4}}'
    )

    echo "Encrypting database backup file $db_backup_file"
    ! aws s3 cp ${s3_bucket}/${db_backup_file} - |
        gpg --no-symkey-cache \
            --output "${db_backup_file}.data" \
            --pinentry-mode=loopback \
            --passphrase "${passphrase}" \
            --symmetric \
            --cipher-algo AES256 -

    # Get the client info backup from the AWS prod backup bucket.
    echo "Finding latest client info backup..."
    client_info_file=$(
        aws s3 ls ${s3_bucket} |
            sort |
            grep client_info |
            tail -n 1 |
            awk '{{print $4}}'
    )

    echo "Encrypting client info backup file $client_info_file"
    ! aws s3 cp ${s3_bucket}/${client_info_file} - |
        gpg --no-symkey-cache \
            --output "${client_info_file}.data" \
            --pinentry-mode=loopback \
            --passphrase "${passphrase}" \
            --symmetric \
            --cipher-algo AES256 -
fi
exit 0
