# Backups

Anika keeps several layers of backup, so that no single failure - a bad deploy, a
deleted bucket, ransomware, or the loss of an AWS region - can take the data with
it. The core layer [streams](../infra/backup.sh) an encrypted
[nightly](../.github/workflows/backup.yml) dump of the production database, plus a
[client-info CSV](../app/core/management/commands/export_client_info.py) kept for
disaster recovery, straight to a private S3 bucket. AWS Backup widens that to the
rest of Anika's production S3 data with an immutable off-region copy, and a
monthly [offline backup](../infra/offline-backup.sh) is pulled out of AWS by hand
as a final backstop. Staging is backed up separately, and unencrypted.

The moving parts at a glance:

| What | Where | When | Retention | Encrypted |
| --- | --- | --- | --- | --- |
| Production database dump + client-info CSV | `anika-database-backups` bucket, Sydney | Nightly (2AM AEST) | Rolling ~30 days | Client-side GPG |
| All production S3 buckets (database dumps, uploaded documents, emails, call audio), via AWS Backup | Sydney vault + immutable air-gapped vault in Melbourne | Daily + monthly | 35 days daily, up to a year monthly | Vault-managed |
| Latest production dump, pulled off AWS | Saved by hand to a local machine | Monthly | Kept manually | GPG (as-is) |
| Staging database dump + client-info CSV | `anika-database-backups-staging` bucket, Sydney | On staging refresh | Rolling ~3 months | None (data is obfuscated) |

Each of these is detailed in the sections below.

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
production](../app/scripts/tasks/staging-restore.sh) and [restoring the
databases to a new server](../infra/setup/restore-databases.sh) - does this
automatically. The only requirement is that whoever (or whatever) performs
the restore has the passphrase available.

The [offline backups script](../infra/offline-backup.sh) includes a convenience
option to decrypt a backup with the user-supplied passphrase.

## Storage

The dumps live in two private S3 buckets, one for production and one for staging,
in the Sydney region. Both keep old object versions, are encrypted at rest by S3,
and block all public access. Both are pruned by an identically-named lifecycle
rule (`expire-old-backups`), but with deliberately different windows: production
keeps a rolling 30 days - current dumps and superseded versions alike - while
staging keeps 90. Production can afford the shorter window because its deeper
history lives in AWS Backup (see below), so the bucket itself stays slim; staging
is not in AWS Backup, so its bucket is its only history and keeps a little more -
cheap, given how little staging holds, and useful for spinning up local dev. That
server-side encryption is only a second layer: because the production dumps are
already GPG-encrypted before upload, the bucket holds nothing but ciphertext that
AWS itself cannot read.

Access is entirely through IAM. The nightly job and the restore scripts sign in
as a single [`clerk-backup`](../infra/offline-backup.sh) user whose keys reach
nothing beyond these two buckets, with just enough permission to list, read and
write backup objects - not to delete them.

## AWS Backup

Alongside the database and client-info CSV dump, [AWS
Backup](https://docs.aws.amazon.com/aws-backup/latest/devguide/whatisbackup.html)
takes managed daily and monthly snapshots of the production S3 buckets
themselves. That widens the safety net well beyond the database: the app's
uploaded documents and call audio are captured too, so the whole of Anika's
production S3 data can be rolled back rather than just the database. It is also
where deeper history lives - the database bucket itself only keeps a rolling
month, so anything older is recovered from these snapshots.

Every snapshot is copied into a locked, [air-gapped
vault](https://docs.aws.amazon.com/aws-backup/latest/devguide/logicallyairgappedvault.html)
whose recovery points cannot be changed or deleted until they age out - the
safeguard against ransomware or an accidental wipe. Production's copy is held in a
second Australian region (Melbourne) for geographic isolation, so backups stay
onshore. Ideally the geography would be reversed - the primary in Melbourne,
where Anika is based, and the air-gapped copy in Sydney - but the Sydney-primary
layout is historical. Staging is deliberately left out of AWS Backup: its data
is obfuscated and can be regenerated from production, so there is nothing there
worth an extra copy.

A monthly AWS Budget (`aws-backup-monthly`) emails tech@anikalegal.org.au if AWS
Backup spend climbs beyond its expected range, so cost drift does not go
unnoticed.