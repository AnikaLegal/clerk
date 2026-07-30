# OpenTofu

Cloud resources described as code with [OpenTofu](https://opentofu.org).
Today this covers only the resources behind the
[restore check](../../docs/restore-check.md); the rest of the AWS account is
still console-managed and documented in [docs/infra.md](../../docs/infra.md)
and [docs/backups.md](../../docs/backups.md). The intent is that new AWS
resources are born here rather than made by hand, so they never need
importing later.

## Layout

Each directory is an independent root with its own remote state in the
`anika-terraform-state` bucket:

| Root | Creates | Applied by | State key |
| --- | --- | --- | --- |
| `bootstrap` | the state bucket itself | admin, once ever | `bootstrap/terraform.tfstate` |
| `restore-check/foundations` | Instance Connect Endpoint, security groups, `restore-check-ci` IAM user and policy | admin, rarely | `restore-check/foundations/terraform.tfstate` |
| `restore-check/run` | the ephemeral check instance | CI, monthly (apply then destroy) | `restore-check/run/terraform.tfstate` |

`foundations` and `run` are separate roots because they have different
lifecycles and credentials: `run` is applied and destroyed by the CI user
every month, and must not contain the resources that define that user - a
misfired destroy would delete its own credentials mid-run. The CI user's S3
access is limited to the `run` state key for the same reason.

## One-time setup

1. Bootstrap the state bucket. This root's own state needs the bucket it
   creates, so the first apply runs on local state and is then migrated -
   the steps are in the header of [bootstrap/main.tf](bootstrap/main.tf).
2. Apply `restore-check/foundations` with admin credentials.
3. Mint the CI access key (kept out of OpenTofu so the secret never enters
   state): `aws iam create-access-key --user-name restore-check-ci`
4. In GitHub Actions, set the repository variables
   `RESTORE_CHECK_EICE_ID`, `RESTORE_CHECK_SUBNET_ID` and
   `RESTORE_CHECK_INSTANCE_SG_ID` from the foundations outputs, plus
   `RESTORE_CHECK_AWS_ACCESS_KEY` and the
   `RESTORE_CHECK_AWS_SECRET_ACCESS_KEY` secret from step 3.

## Conventions

- Pin versions: each root pins `required_version` and the AWS provider.
  Commit the `.terraform.lock.hcl` provider lock file a root's first
  `tofu init` generates.
- No secrets in state or user data: access keys are minted manually, never
  as `aws_iam_access_key` resources, and secrets reach the check instance
  over SSH stdin only. Both user data and state are readable to anyone with
  access to the API or the state bucket.
- Never `tofu destroy` in `bootstrap` or `foundations` unless
  decommissioning the restore check entirely.
