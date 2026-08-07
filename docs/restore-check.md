# Restore checks

Our Cybersecurity Governance Policy and Business Continuity Plan require
regular restore tests of our backups - at least twice per year - with the
results recorded and reported to senior management (see TEC-1987 in Linear).
All checks run against **production** backups: the point is to prove that
production can be recovered, and a test against anything else can silently
diverge from that.

Each run's result summary is posted, with a pass/fail headline, to Slack.
Failures mean the latest backup may not be restorable and should be
investigated immediately.

## Monthly: automated database restore check

The check runs entirely inside AWS - GitHub is not involved - at 4AM
Melbourne time on the 1st of each month: an EventBridge schedule invokes
the `restore-check-db` [Lambda durable
function](https://docs.aws.amazon.com/lambda/latest/dg/durable-functions.html)
([db-lambda.py](../infra/restore-check/db-lambda.py)), which:

1. Launches an ephemeral Fargate task from the `restore-check-db` ECR
   image - a throwaway Postgres of the pinned major plus the check script
   ([Dockerfile.database](../infra/restore-check/Dockerfile.database)) -
   and suspends, free of charge, until the task stops.
2. Reads the results back out of the task's log stream and posts the
   report to Slack ([report.py](../infra/restore-check/report.py)).
3. Checks in against a Sentry cron monitor as it goes, the dead-man
   switch behind the whole pipeline: a run that never starts, dies
   partway, or fails alerts through Sentry's alert rules.

Production data only ever exists inside the task, which accepts no
inbound connections of any kind (no SSH, no ECS Exec) and dies with the
run. Failsafes nest: a `timeout` entrypoint kills a wedged check at 90
minutes, the Lambda gives up and stops the task at ~100, and the durable
execution itself times out at 2 hours.

The check itself ([db-check.py](../infra/restore-check/db-check.py)) verifies:

- the latest dump is recent, i.e. nightly backups are actually being taken
- `pg_restore` completes with zero errors
- restored row counts match the manifest [backup.sh](../infra/backup.sh)
  writes at dump time (within a small tolerance for round-the-clock churn)
- the client info CSV decrypts and parses

All supporting resources - the schedule, the Lambda, the ECS cluster and
task definition, the ECR repository, the IAM roles, and the Sentry
monitor with its alert rule - are defined as code in
[infra/tofu/restore-check/foundations](../infra/tofu/restore-check/foundations)
(see the [infra/tofu README](../infra/tofu/README.md) for one-time
setup). The only hand-made pieces are three SecureString SSM parameters,
kept out of code so no secret enters the public repo or OpenTofu state:

| Parameter | Purpose |
| --- | --- |
| `/backup/passphrase` | decrypts the backups; injected into the container by ECS (same value as BitWarden and the nightly backup's GitHub secret) |
| `/backup/alerts-slack-webhook` | the incoming webhook for the backup-alerts Slack channel; read by the Lambda only |
| `/restore-check-db/sentry-cron-url` | the Sentry monitor's check-in URL, built from the clerk project DSN |

Operating it:

- **Run it by hand**: `aws lambda invoke --function-name
  restore-check-db:live --invocation-type Event --payload '{}'
  /dev/stdout`
- **Watch a run**: the step-by-step execution timeline is in the Lambda
  console under Durable executions; the full check log is in the
  CloudWatch log group `/restore-check/db` (the Slack report footer links
  straight to it).
- **Change the check**: edit under `infra/restore-check/` and run
  `just restore-check-db-image` - the task pulls `:latest`, so the push
  alone deploys it. Changes to db-lambda.py, report.py or the tofu need a
  foundations apply instead.
- **Alerting**: Slack carries every run's result table; Sentry alerts
  when a run is missed, times out, or fails. The monitor's schedule
  mirrors the EventBridge schedule in tofu - change both together.

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
