# Foundations for the restore checks (TEC-1987): the shared plumbing that
# the per-check files in this root (db.tf, and in future the S3 check)
# build on. Applied rarely, by a human with admin AWS credentials and the
# Sentry token exported (see ../../README.md):
#
#   export SENTRY_AUTH_TOKEN=...
#   tofu -chdir=infra/tofu/restore-check/foundations init
#   tofu -chdir=infra/tofu/restore-check/foundations apply

terraform {
  required_version = ">= 1.10"

  required_providers {
    aws = {
      # 6.25 is the first release with aws_lambda_function durable_config.
      source  = "hashicorp/aws"
      version = "~> 6.25"
    }

    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.4"
    }

    sentry = {
      source  = "jianyuan/sentry"
      version = "~> 0.15"
    }
  }

  backend "s3" {
    bucket       = "anika-terraform-state"
    key          = "restore-check/foundations/terraform.tfstate"
    region       = "ap-southeast-2"
    use_lockfile = true
  }
}

provider "aws" {
  region = local.region

  default_tags {
    tags = {
      Purpose = "restore-check"
    }
  }
}

# Authenticates via the SENTRY_AUTH_TOKEN environment variable: the token
# of the "Clerk OpenTofu" internal integration, held in Anika BitWarden - owned
# by the organization rather than any user account. Creation steps and
# permissions are in ../../README.md (one-time setup). Export it before
# running plan or apply (validate needs no token).
provider "sentry" {}

locals {
  region = "ap-southeast-2"
}

data "aws_caller_identity" "current" {}

# The default VPC, and a deterministic subnet within it for the check
# tasks: no ingress ever, a public IP for egress only (S3, ECR, logs).
data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

locals {
  subnet_id = sort(data.aws_subnets.default.ids)[0]
}
