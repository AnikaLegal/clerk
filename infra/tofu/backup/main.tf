# The AWS Backup scheme (see docs/backups.md): daily and monthly snapshots
# of the production S3 buckets into the Sydney vault, every one copied to
# the locked, logically air-gapped vault in Melbourne. Imported from the
# console-built originals in August 2026 (TEC-2063 groundwork) - the
# import blocks at the bottom adopted the live resources unchanged.
#
# Applied rarely, by a human with admin AWS credentials:
#
#   tofu -chdir=infra/tofu/backup init
#   tofu -chdir=infra/tofu/backup apply
#
# Deliberately NOT managed here:
#
# - The backup PLAN (anika-clerk-backup-plan, 906b97d2): the AWS provider
#   cannot express two of its live settings - the S3 IndexActions on both
#   rules (hashicorp/terraform-provider-aws#40672) and the S3
#   AdvancedBackupSettings (BackupACLs/BackupObjectTags "enabled", which
#   the media buckets' public-read ACLs depend on; the provider only
#   accepts EC2 there). Managing the plan would strip both on the next
#   apply. It stays console-managed until the provider catches up; its
#   rules are documented in docs/backups.md.
# - The Default vaults (AWS-made) and the leftover anika-clerk-staging-*
#   vaults in Sydney (their plan was removed in July 2026 - the plain one
#   awaits deletion, the locked air-gapped one must wait for its recovery
#   points to age out).
# - The console-created AWSBackupDefaultServiceRole the selection runs as
#   (referenced by ARN).

terraform {
  required_version = ">= 1.10"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.25"
    }
  }

  backend "s3" {
    bucket       = "anika-terraform-state"
    key          = "backup/terraform.tfstate"
    region       = "ap-southeast-2"
    use_lockfile = true
  }
}

provider "aws" {
  region = "ap-southeast-2"
}

# The air-gapped copies live in a second Australian region for geographic
# isolation (see docs/backups.md for why the geography is this way round).
provider "aws" {
  alias  = "melbourne"
  region = "ap-southeast-4"
}

data "aws_caller_identity" "current" {}

locals {
  # The console-managed backup plan (anika-clerk-backup-plan) - see the
  # header for why the plan itself is not a resource here.
  backup_plan_id = "906b97d2-b408-4626-b009-52df4b75a23e"

  # The production buckets AWS Backup protects. The restore checks read
  # this list too - it is the single source of truth for what "all
  # protected buckets" means.
  protected_buckets = [
    "anika-clerk",
    "anika-database-backups",
    "anika-emails",
    "anika-twilio-audio",
  ]
}

# --- Vaults --------------------------------------------------------------------

resource "aws_backup_vault" "clerk" {
  name        = "anika-clerk-backup-vault"
  kms_key_arn = "arn:aws:kms:ap-southeast-2:${data.aws_caller_identity.current.account_id}:key/2af29e79-8209-4409-8b30-5259f70adb35"
}

# Locked on creation: recovery points cannot be changed or deleted until
# they age out, and min/max retention are immutable - the ransomware and
# accidental-wipe safeguard.
resource "aws_backup_logically_air_gapped_vault" "clerk" {
  provider = aws.melbourne

  name               = "anika-clerk-logically-air-gapped-vault"
  min_retention_days = 7
  max_retention_days = 730
}

# --- The selection -------------------------------------------------------------

# Which resources the (console-managed, see header) backup plan protects.
resource "aws_backup_selection" "s3" {
  plan_id      = local.backup_plan_id
  name         = "anika-clerk-s3-buckets"
  iam_role_arn = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/service-role/AWSBackupDefaultServiceRole"

  resources = [for bucket in local.protected_buckets : "arn:aws:s3:::${bucket}"]
}

# --- Adoption of the console-built originals ------------------------------------

import {
  to = aws_backup_vault.clerk
  id = "anika-clerk-backup-vault"
}

import {
  to       = aws_backup_logically_air_gapped_vault.clerk
  id       = "anika-clerk-logically-air-gapped-vault"
  provider = aws.melbourne
}

import {
  to = aws_backup_selection.s3
  id = "906b97d2-b408-4626-b009-52df4b75a23e|4ddcc413-7f20-446e-a32d-d61ad81ffd8a"
}

# --- Outputs for the restore checks (infra/tofu/restore-check) ------------------

output "protected_buckets" {
  value = local.protected_buckets
}

output "backup_plan_id" {
  value = local.backup_plan_id
}

output "vault_arn" {
  value = aws_backup_vault.clerk.arn
}

output "air_gapped_vault_arn" {
  value = aws_backup_logically_air_gapped_vault.clerk.arn
}
