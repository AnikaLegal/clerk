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
| `restore-check/foundations` | everything behind the [restore check](../../docs/restore-check.md): schedule, Lambda, ECS cluster and task definition, ECR repository, IAM roles, Sentry cron monitor and alert | admin, rarely | `restore-check/foundations/terraform.tfstate` |

## One-time setup

1. Bootstrap the state bucket. This root's own state needs the bucket it
   creates, so the first apply runs on local state and is then migrated -
   the steps are in the header of [bootstrap/main.tf](bootstrap/main.tf).
2. Create the Sentry internal integration whose token OpenTofu uses to
   manage the restore check's cron monitor and alert rule. Once, in the
   Sentry UI, as an org Owner or Manager:
   1. Settings > Developer Settings > Custom Integrations > Create New
      Integration > Internal Integration.
   2. Name it `Clerk OpenTofu`. Leave everything else empty - no webhook URL,
      no redirect URL, no UI components, no webhook event boxes. It
      exists only to mint an API token.
   3. Set the permissions. The form varies: newer ones have an Alerts
      row, older ones do not. Cron monitors and alert rules accept
      either set:

      | Permission | With an Alerts row | Without one |
      | --- | --- | --- |
      | Project | Read | Read & Write |
      | Team | Read | Read |
      | Organization | Read | Read & Write |
      | Alerts | Read & Write | not offered |
      | everything else | No Access | No Access |

      If a `tofu plan` ever returns 403, the error names the missing
      scope - edit the integration's permissions, which its existing
      tokens inherit.
   4. Save, then open the integration's Tokens section, create a token
      (New Token) and copy it into Anika BitWarden - it is only shown at
      creation. Tokens never expire; revoke and re-mint from the same
      screen if one ever leaks. The auto-generated client secret is for
      verifying webhook signatures and is not used here - no need to
      save it.
3. Apply `restore-check/foundations` with admin AWS credentials and the
   Sentry token exported: `export SENTRY_AUTH_TOKEN=...` (plan and apply
   need it; validate does not).
4. Create the three SecureString parameters by hand, so no secret ever
   enters state or the public repo - the values and commands are in the
   header of
   [restore-check/foundations/db.tf](restore-check/foundations/db.tf).
5. Build and push the check image: `just restore-check db-image`.

## Conventions

- Pin versions: each root pins `required_version` and the AWS provider.
  Commit the `.terraform.lock.hcl` provider lock file a root's first
  `tofu init` generates.
- No secrets in state: secrets live in hand-created SSM SecureString
  parameters, never in OpenTofu resources - ECS injects the passphrase
  into the check container, and the Lambda reads the webhook and Sentry
  URL at run time. State is readable to anyone with access to the state
  bucket (and this repo is public), so treat both accordingly.
- Never `tofu destroy` in `bootstrap` or `foundations` unless
  decommissioning the restore check entirely.
