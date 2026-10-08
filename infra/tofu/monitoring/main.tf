# Sentry monitoring for Clerk (TEC-2264): uptime monitors on the site,
# Clerk and the intake form, and the alerts for outages and new issues.
# Change them here, not in the Sentry UI: the next apply reverts UI edits.
# Applied by a human with AWS credentials for the state bucket and the
# Sentry token exported (see ../README.md):
#
#   export SENTRY_AUTH_TOKEN=...
#   tofu -chdir=infra/tofu/monitoring init
#   tofu -chdir=infra/tofu/monitoring apply

terraform {
  required_version = ">= 1.10"

  required_providers {
    sentry = {
      source  = "jianyuan/sentry"
      version = "~> 0.15"
    }
  }

  backend "s3" {
    bucket       = "anika-terraform-state"
    key          = "monitoring/terraform.tfstate"
    region       = "ap-southeast-2"
    use_lockfile = true
  }
}

# Authenticates via SENTRY_AUTH_TOKEN: the "Clerk OpenTofu" internal
# integration's token (see ../README.md).
provider "sentry" {}

locals {
  organization = "anika-legal"

  # The tech@ Sentry user. Alerts email it directly: it has issue alert
  # notifications turned off, which silences team-addressed email.
  tech_user_id = "441920"

  # The Linear Sentry app, and the Tech team and Triage status the issues
  # it creates land in.
  linear_app_id   = "3216"
  linear_team_id  = "5d330bf8-c6a4-4d8d-97ad-3a8127399ac8"
  linear_state_id = "9555b108-c80b-43f3-9bcb-03ef3cb4e613"

  environments = {
    production = {
      hosts = {
        site   = "anikalegal.org.au"
        intake = "intake.anikalegal.org.au"
      }
      slack_channel   = { name = "sentry", id = "CLW19LWTH" }
      linear_label_id = "675d7ecf-c114-45fa-8fb0-e53342fecd3d" # Production
    }
    staging = {
      hosts = {
        site   = "staging.anikalegal.org.au"
        intake = "intake-staging.anikalegal.org.au"
      }
      slack_channel   = { name = "sentry_test", id = "CLW19N0P9" }
      linear_label_id = "5aaa9540-ccc9-4e1e-8d66-5fcd2ce2b372" # Staging
    }
  }
}

data "sentry_organization_integration" "slack" {
  organization = local.organization
  provider_key = "slack"
  name         = "Anika Legal"
}
