# Bootstrap root: the S3 bucket that stores OpenTofu state for every other
# root under infra/tofu. Applied once, ever.
#
# This root has a chicken-and-egg problem: its own state needs the bucket it
# creates. First time only (in a fresh AWS account, with the backend block
# below commented out):
#
#   1. tofu -chdir=infra/tofu/bootstrap init
#      tofu -chdir=infra/tofu/bootstrap apply     (state is written locally)
#   2. Uncomment the backend block.
#   3. tofu -chdir=infra/tofu/bootstrap init -migrate-state
#      (the local state moves into the bucket it describes; delete the
#      leftover local terraform.tfstate* files afterwards)
#
# This was done for the current account on 2026-07-29; the backend below is
# live.

terraform {
  required_version = ">= 1.10"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }

  backend "s3" {
    bucket       = "anika-terraform-state"
    key          = "bootstrap/terraform.tfstate"
    region       = "ap-southeast-2"
    use_lockfile = true
  }
}

provider "aws" {
  region = "ap-southeast-2"
}

resource "aws_s3_bucket" "state" {
  bucket = "anika-terraform-state"

  # State is the record of what exists: losing it means importing everything
  # back by hand.
  lifecycle {
    prevent_destroy = true
  }
}

# Keep old state versions so a bad write can be rolled back.
resource "aws_s3_bucket_versioning" "state" {
  bucket = aws_s3_bucket.state.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_public_access_block" "state" {
  bucket                  = aws_s3_bucket.state.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
