#!/usr/bin/env bash

set -o errexit
set -o pipefail

s3_bucket="s3://anika-database-backups"
prog="$(basename $BASH_SOURCE)"
usage="Usage: ${prog} [OPTIONS]

OPTIONS
  -d, --decrypt <FILE>  Decrypt the supplied offline backup file.
  -h, --help            Show this help.
  
When no options are supplied the latest (already encrypted) backup files will be
downloaded from AWS to the current directory."

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
    read -r -s -p $'Enter Clerk backup passphrase:\n' passphrase

    echo "Decrypting backup file $decrypt_file"
    # Strip the encrypted-file suffix.
    output="${decrypt_file%.gpg}"
    gpg --no-symkey-cache --output "${output}" --pinentry-mode=loopback \
        --passphrase "${passphrase}" --decrypt "$decrypt_file"
else
    # Read required secret. Key in Anika BitWarden.
    read -r -s -p $'Enter AWS backup user secret access key:\n' AWS_SECRET_ACCESS_KEY
    export AWS_ACCESS_KEY_ID="AKIAUZ6OTSVMUXQAJLGM"
    export AWS_SECRET_ACCESS_KEY

    # Prod backups are already GPG-encrypted at rest, so just download them as-is.
    # Decrypt later with: ${prog} -d <FILE>

    # Get the db backup from the AWS prod backup bucket. Each dump has a
    # row count manifest next to it which must not match here.
    echo "Finding latest database backup..."
    db_backup_file=$(
        aws s3 ls ${s3_bucket} |
            sort |
            grep postgres_clerk |
            grep -v manifest |
            tail -n 1 |
            awk '{{print $4}}'
    )

    echo "Downloading database backup file $db_backup_file"
    aws s3 cp ${s3_bucket}/${db_backup_file} "${db_backup_file}"

    # Get the dump's row count manifest too: it says what a successful
    # restore of this backup should contain.
    manifest_file="${db_backup_file%.gpg}"
    manifest_file="${manifest_file%.sql}.manifest.json"
    echo "Downloading manifest file $manifest_file"
    aws s3 cp ${s3_bucket}/${manifest_file} "${manifest_file}" ||
        echo "No manifest found for ${db_backup_file}, skipping"

    # Get the client info backup from the AWS prod backup bucket.
    echo "Finding latest client info backup..."
    client_info_file=$(
        aws s3 ls ${s3_bucket} |
            sort |
            grep client_info |
            tail -n 1 |
            awk '{{print $4}}'
    )

    echo "Downloading client info backup file $client_info_file"
    aws s3 cp ${s3_bucket}/${client_info_file} "${client_info_file}"
fi
exit 0
