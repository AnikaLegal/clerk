# Restore checks

Our Cybersecurity Governance Policy and Business Continuity Plan require
regular restore tests of our backups - at least twice per year - with the
results recorded and reported to senior management (see TEC-1987 in Linear).
All checks run against **production** backups: the point is to prove that
production can be recovered, and a test against anything else can silently
diverge from that.

Each run's result summary is published on the workflow run in GitHub
Actions and posted, with a pass/fail headline, to Slack. Failures mean the
latest backup may not be restorable and should be investigated immediately.

## Monthly: automated database restore check

The [restore-check.yml](../.github/workflows/restore-check.yml) workflow
runs monthly (and on demand via workflow_dispatch). The CI runner only
orchestrates: production data only ever exists on the ephemeral instance,
inside our infrastructure, and the live server is not involved at all - a
real recovery restores onto fresh compute, so that is what gets tested.
[run.sh](../infra/restore-check/run.sh):

1. Applies the OpenTofu root at
   [infra/tofu/restore-check/run](../infra/tofu/restore-check/run) to launch
   an ephemeral EC2 instance in our AWS account, with the pinned Postgres
   major installed and a self-terminate failsafe.
2. Connects over SSH through an EC2 Instance Connect Endpoint - an
   IAM-authenticated tunnel to the instance's private address, so the
   instance accepts no connections from the internet and the per-run SSH
   key never leaves the runner.
3. Runs the check on the instance, streaming its output back.
4. Destroys the instance, and the production data with it. Remote state
   means even resources orphaned by a crashed run are swept up by the next
   one.

The check itself ([check.py](../infra/restore-check/check.py)) verifies:

- the latest dump is recent, i.e. nightly backups are actually being taken
- `pg_restore` completes with zero errors
- restored row counts match the manifest [backup.sh](../infra/backup.sh)
  writes at dump time (within a small tolerance for round-the-clock churn)
- the client info CSV decrypts and parses

The runner receives only the check summary (statuses and row counts), which
it publishes on the workflow run and
[report.sh](../infra/restore-check/report.sh) posts to Slack.

The workflow is configured through GitHub Actions variables and secrets:

| Name | Kind | Purpose |
| --- | --- | --- |
| `AWS_BACKUP_USER_ACCESS_KEY`, `AWS_BACKUP_USER_SECRET_ACCESS_KEY` | variable, secret | `clerk-backup` credentials: the instance reads the backup bucket (pre-existing) |
| `BACKUP_PASSPHRASE` | secret | decrypts the backups (pre-existing) |
| `RESTORE_CHECK_AWS_ACCESS_KEY`, `RESTORE_CHECK_AWS_SECRET_ACCESS_KEY` | variable, secret | `restore-check-ci` credentials: the runner manages the ephemeral instance |
| `RESTORE_CHECK_EICE_ID` | variable | the Instance Connect Endpoint id |
| `RESTORE_CHECK_SUBNET_ID` | variable | the launch subnet id |
| `RESTORE_CHECK_INSTANCE_SG_ID` | variable | the instance security group id |
| `BACKUP_ALERTS_SLACK_WEBHOOK_URL` | secret | the incoming webhook for the backup-alerts Slack channel |

The supporting cloud resources - the Instance Connect Endpoint, security
groups, the `restore-check-ci` user and its policy, and the OpenTofu state
bucket - are defined as code under [infra/tofu](../infra/tofu); the three id
variables are outputs of its foundations root. See its
[README.md](../infra/tofu/README.md) for the one-time setup.

## Quarterly: S3 restore check

Planned, not yet built: restore the media buckets from an AWS Backup recovery
point into a scratch bucket and verify a sample of objects, with at least one
run per year restoring from the air-gapped vault copy in Melbourne.

## Bi-annually: full rebuild rehearsal

A recurring [Linear
issue](https://linear.app/anika-legal/issue/TEC-2044/bi-annual-restore-rehearsal)
schedules a full disaster recovery rehearsal every 6 months. The full
checklist lives on the issue; in outline:

1. Retrieve the secrets from BitWarden - this deliberately tests the human
   path the automation cannot.
2. Provision a throwaway EC2 instance with
   [provision.sh](../infra/setup/provision.sh).
3. Deploy the staging environment with
   [init-env.sh](../infra/setup/init-env.sh).
4. Restore both databases with
   [restore-databases.sh](../infra/setup/restore-databases.sh).
5. Verify, and record the results on the issue.
6. Tear everything down.

Isolation rules for rehearsals:

- Never target the current live server - the scripts refuse.
- Restoring the production database is the point of the exercise, but never
  deploy the production application stack or its credentials on the
  throwaway host: only the staging stack runs there, so nothing acts on the
  restored production data or reaches real external services (email, Slack,
  Microsoft).
- Keep the host up only as long as needed.
- Confirm teardown with a tag sweep.

## History

The process was established in July 2026. The provisioning and restore flow
was verified end to end on throwaway hosts on 2026-07-17 (TEC-2035, which also
surfaced and fixed several latent defects) and 2026-07-23 (TEC-2038). Those
runs restored staging backups; from the first automated run onward, checks
run against production backups.
