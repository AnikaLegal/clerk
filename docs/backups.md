# Backups

[Nightly scheduled backups](../.github/workflows/backup.yml) of the production
PostgreSQL database and a [client-info
CSV](../app/core/management/commands/export_client_info.py) (kept for disaster
recovery) are [dumped and streamed](../infra/backup.sh) straight to a private S3
backup bucket, with no plaintext copy touching disk on the way. 

Monthly [offline backups](../infra/offline-backup.sh) are saved manually. They
are simply the latest already-encrypted production backups downloaded as-is.

## Encryption

Production backups are encrypted on the client side before they reach S3: the
dump is run through a symmetric GPG cipher (AES256) under a single passphrase,
so the bucket only ever holds ciphertext that AWS itself cannot read. The same
passphrase decrypts the backup when it is restored.

- Encryption is on by default for production backups.
- Staging data is obfuscated rather than real, so staging backups are
  deliberately left unencrypted.
- The passphrase is held in Anika BitWarden and mirrored into the CI secret used
  by the backup job; the two must stay in sync. Lose the passphrase and the
  backups are unrecoverable.

## Staging

The staging environment is [regenerated manually from
production](../.github/workflows/staging.yml).  As part of that refresh its data
is [automatically
obfuscated](../app/core/management/commands/obfuscate_data.py), and staging then
produces the same backups as production - to its own separate bucket - except
those backups are left unencrypted.  Because the data is already obfuscated
there is no PII to protect, and keeping it in the clear makes it easy to
[populate a local development environment](../app/scripts/tasks/dev-restore.sh)
from the staging backups.

## Restoring

An encrypted backup must be decrypted with the passphrase before it can be
loaded back into PostgreSQL. Each restore path - [refreshing staging from
production](../app/scripts/tasks/staging-restore.sh), and [migrating to a new
server](../infra/setup/migrate.sh) - does this automatically. The only 
requirement is that whoever (or whatever) performs the restore has the
passphrase available.

The [offline backups script](../infra/offline-backup.sh) includes a convenience
option to decrypt a backup with the user-supplied passphrase.