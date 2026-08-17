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

- **Run it by hand**: `just restore-check db` (needs AWS credentials
  that may invoke the Lambda).
- **Watch a run**: the step-by-step execution timeline is in the Lambda
  console under Durable executions; the full check log is in the
  CloudWatch log group `/restore-check/db` (the Slack report footer links
  straight to it).
- **Change the check**: edit under `infra/restore-check/` and run
  `just restore-check db-image` - the task pulls `:latest`, so the push
  alone deploys it. Changes to db-lambda.py, report.py or the tofu need a
  foundations apply instead.
- **Alerting**: Slack carries every run's result table; Sentry alerts
  when a run is missed, times out, or fails. The monitor's schedule
  mirrors the EventBridge schedule in tofu - change both together.

## Monthly: automated S3 restore check

Whether the AWS Backup snapshots of the production buckets *land* is
asserted every morning by the daily landing check (see
[backups.md](./backups.md#aws-backup)); this check proves they *restore*.
AWS Backup [restore
testing](https://docs.aws.amazon.com/aws-backup/latest/devguide/restore-testing.html)
plans restore each protected bucket's latest recovery point into a
scratch bucket the service creates and later deletes
(`awsbackup-restore-test-*`): the Sydney vault monthly at 5AM Melbourne
time on the 1st, the air-gapped Melbourne vault quarterly
(Jan/Apr/Jul/Oct). Two Lambdas turn those restores into a verdict:

1. [s3-validate-lambda.py](../infra/restore-check/s3-validate-lambda.py)
   runs once per completed restore job - the documented EventBridge
   validation hook; Melbourne's events forward cross-region to the same
   rule. It compares the restored bucket against the live one (every
   object older than the recovery point must be present with matching
   size, drift since the snapshot is tolerated), fetches 25 sampled
   objects end to end, and stamps SUCCESSFUL or FAILED onto the job with
   `PutRestoreValidationResult`.
2. [s3-report-lambda.py](../infra/restore-check/s3-report-lambda.py), a
   Lambda durable function like the db check's, runs at noon the same
   day: it suspends until every job is finished and validated (giving up
   after ~6 hours), asserts that every protected bucket actually produced
   a restore job - a bucket AWS Backup silently skipped is a failure, not
   a missing row - and posts one Slack table covering both vaults. The
   `restore-check-s3` Sentry cron monitor stands behind it as the
   dead-man switch.

The protected-bucket list comes from the
[infra/tofu/backup](../infra/tofu/backup/main.tf) root, so a bucket added
to the backup selection is automatically restore-tested too. Everything
is defined in the same foundations root as the db check, plus one more
hand-made SecureString parameter, `/restore-check-s3/sentry-cron-url`.

Operating it:

- **Run the report by hand**: `just restore-check s3` - it reports on
  whatever restore jobs the last 24 hours produced (with none, every
  bucket rows up as FAIL, which is itself the honest answer).
- **Start a restore test off-schedule**: there is no on-demand start for
  a restore testing plan; temporarily move its `schedule_expression` a
  few minutes ahead with `aws backup update-restore-testing-plan`, let it
  fire, then `tofu apply` to put the schedule back.
- **Watch a run**: restore jobs (type Test) and their validation verdicts
  are on the Backup console's restore jobs page; the validator's log is
  in the `/aws/lambda/restore-check-s3-validate` log group.
- **Costs**: restore testing bills per evaluated recovery point, plus a
  few days of scratch-bucket storage until the service's cleanup
  lifecycle deletes it - cents at our scale.

## Bi-annually: full rebuild rehearsal

A [recurring Linear
issue](https://linear.app/anika-legal/settings/teams/TEC/recurring-issues/afc1fbf9-9beb-44bb-a9cc-cef4fd718913/edit)
(managed under the Tech team's [recurring issues
settings](https://linear.app/anika-legal/settings/teams/TEC/recurring-issues/))
schedules a full disaster recovery rehearsal every 6 months, spawning an
instance issue with the drill checklist each time. Unlike the
monthly checks it is deliberately human-driven: the point is proving a
person can go from the BitWarden secrets to a rebuilt, restored
environment. The mechanics are automated as the `rehearsal` just module
([infra/rehearsal](../infra/rehearsal/justfile) plus the ephemeral
[infra/tofu/rehearsal](../infra/tofu/rehearsal/main.tf) root, which holds
nothing between drills). The full checklist lives on the issue; in
outline:

1. Retrieve the secrets from BitWarden and prove they work (fresh clone +
   transcrypt unlock) - this deliberately tests the human path the
   automation cannot.
2. `just rehearsal up` - a throwaway EC2 host, SSH from your IP only,
   armed with a 4-hour self-destruct so production data cannot sit on a
   forgotten host. A long drill can disarm it on the host
   (`systemctl stop rehearsal-self-destruct.timer`) and re-arm with a new
   deadline (the `systemd-run` line in
   [user-data.yml.tftpl](../infra/tofu/rehearsal/user-data.yml.tftpl)) -
   do this deliberately, not by default.

   The host trusts for root the union of `~/.ssh/id_ed25519.pub`
   (if present) and every key your ssh agent serves (`ssh-add -L`) - so
   whichever of them ssh ends up offering, a matching key is on the
   host; set `REHEARSAL_SSH_KEY` to a public key file to install exactly
   that key instead. `ssh-add` only sees the agent at `$SSH_AUTH_SOCK` -
   if your keys live in a different agent (a password manager's, say),
   point that variable at its socket in the drill shell first.
3. Confirm your SSH auth needs no prompting: the stack deploy runs
   Docker over SSH, which cannot answer a key passphrase prompt, so
   signing must come from an agent that holds your key (or a
   passphrase-less key). The test is that `ssh root@<drill ip> true`
   runs silently, first try. If it prompts instead:
   - No agent, or the key is not loaded: `ssh-add ~/.ssh/<key>`.
   - Key held by an agent, still prompting: something in `~/.ssh/config`
     points the host at a different agent - `ssh -G <ip> | grep -i
     identityagent` shows which. Either move the key into that agent
     (password managers' agents approve through their own UI, which
     works where terminal prompts cannot), or override it for the drill
     host with a block *above* the global entry (ssh uses the first
     value it finds per option):

     ```
     Host <drill host IP>       # update each drill; `up` prints the IP
         IdentityAgent SSH_AUTH_SOCK
     ```
4. `just rehearsal setup <ip>` -
   [provision.sh](../infra/setup/provision.sh) then the staging stack via
   [init-env.sh](../infra/setup/init-env.sh) (staging only; the recipe
   accepts no other environment).
5. `just rehearsal restore <ip>` -
   [restore-databases.sh](../infra/setup/restore-databases.sh), which
   prompts for the backup credentials and passphrase.
6. `just rehearsal verify <ip>` - row counts against the manifest of the
   dump that was actually restored (exact match), the staging app
   answering through nginx, and the Sentry blackhole holding inside the
   containers; prints the results block to paste onto the Linear issue.
7. `just rehearsal down` - destroys the host and then *asserts* nothing
   tagged `Purpose=rehearsal` remains (`just rehearsal sweep` re-runs the
   assertion alone any time).
8. Report the outcome to senior management, then close the issue.

The drill runs in its own throwaway VPC - sharing nothing with the live
server's network - where a private DNS zone blackholes `sentry.io`, so
the drill's staging workers cannot leak errors into the real staging
Sentry project. Both exist only while a drill host does. The blackhole
only covers DNS inside the VPC: browser-side JS events from anyone
viewing the drill site resolve normally and would still reach Sentry.
Only the operator ever loads the site, so that residue is accepted.

Isolation rules for rehearsals:

- Never target the current live server - the scripts refuse.
- Restoring the production database is the point of the exercise, but never
  deploy the production application stack or its credentials on the
  throwaway host: only the staging stack runs there, so nothing acts on the
  restored production data or reaches real external services (email, Slack,
  Microsoft).
- Keep the host up only as long as needed.
- Confirm teardown with a tag sweep.
