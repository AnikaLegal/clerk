# One-time foundations for the restore check (TEC-1987): the standing,
# free-of-charge resources that the monthly run root
# (infra/tofu/restore-check/run) launches its ephemeral instance into.
#
# Applied rarely, by a human with admin credentials:
#
#   tofu -chdir=infra/tofu/restore-check/foundations init
#   tofu -chdir=infra/tofu/restore-check/foundations apply
#
# The outputs at the bottom map to GitHub Actions repository variables (see
# docs/restore-check.md). The restore-check-ci access key is deliberately
# NOT managed here: an aws_iam_access_key resource would write the secret
# key into the state file. Mint it manually
# (aws iam create-access-key --user-name restore-check-ci) and store it in
# the GitHub repository variable and secret.

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

# Authenticates via the SENTRY_AUTH_TOKEN environment variable: an
# org-scoped API token held in Anika BitWarden. Export it before running
# plan or apply (validate needs no token).
provider "sentry" {}

locals {
  region       = "ap-southeast-2"
  state_bucket = "anika-terraform-state"
}

data "aws_caller_identity" "current" {}

# The default VPC, and a deterministic subnet within it: the Instance
# Connect Endpoint is bound to a single subnet, and the run root launches
# the instance into that same subnet.
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

# The instance accepts SSH from the endpoint alone: a VPC-internal rule, so
# nothing is reachable from the internet. Egress stays open for apt and S3.
resource "aws_security_group" "instance" {
  name        = "restore-check-instance"
  description = "Restore check instance: SSH from the Instance Connect Endpoint only"
  vpc_id      = data.aws_vpc.default.id
}

resource "aws_security_group" "endpoint" {
  name        = "restore-check-endpoint"
  description = "EC2 Instance Connect Endpoint for the restore check"
  vpc_id      = data.aws_vpc.default.id
}

resource "aws_vpc_security_group_ingress_rule" "instance_ssh_from_endpoint" {
  security_group_id            = aws_security_group.instance.id
  ip_protocol                  = "tcp"
  from_port                    = 22
  to_port                      = 22
  referenced_security_group_id = aws_security_group.endpoint.id
}

resource "aws_vpc_security_group_egress_rule" "instance_all_out" {
  security_group_id = aws_security_group.instance.id
  ip_protocol       = "-1"
  cidr_ipv4         = "0.0.0.0/0"
}

resource "aws_vpc_security_group_egress_rule" "endpoint_ssh_to_instance" {
  security_group_id            = aws_security_group.endpoint.id
  ip_protocol                  = "tcp"
  from_port                    = 22
  to_port                      = 22
  referenced_security_group_id = aws_security_group.instance.id
}

# The Instance Connect Endpoint: an IAM-authenticated, CloudTrail-audited
# SSH tunnel to the instance's private address, replacing public SSH,
# standing key pairs and IP allowlisting. Free of charge.
resource "aws_ec2_instance_connect_endpoint" "restore_check" {
  subnet_id          = local.subnet_id
  security_group_ids = [aws_security_group.endpoint.id]

  # AWS defaults this to true, which would deliver tunnelled traffic with
  # the client's own source address - the instance security group only
  # admits traffic from the endpoint's security group, so SSH would be
  # dropped. False also means the check does not depend on runner IPs.
  preserve_client_ip = false

  tags = {
    Name = "restore-check"
  }
}

# The CI user that .github/workflows/restore-check.yml runs as.
resource "aws_iam_user" "ci" {
  name = "restore-check-ci"
}

# A managed policy rather than an inline one: the policy document is larger
# than the 2048 byte inline limit (managed policies allow 6144).
resource "aws_iam_policy" "ci" {
  name   = "restore-check-ci"
  policy = data.aws_iam_policy_document.ci.json
}

resource "aws_iam_user_policy_attachment" "ci" {
  user       = aws_iam_user.ci.name
  policy_arn = aws_iam_policy.ci.arn
}

# What the CI user may do, and no more: launch and terminate instances
# tagged Purpose=restore-check, tunnel to them through the endpoint, push an
# ephemeral SSH key, and manage the run root's own state. Deliberately
# absent: security group and key pair writes (those are standing resources
# defined here), all of iam:*, ssm parameter writes, and any access to the
# backup bucket (the check instance receives the clerk-backup credentials
# over SSH stdin instead).
data "aws_iam_policy_document" "ci" {
  statement {
    sid       = "DescribeEc2"
    actions   = ["ec2:Describe*"]
    resources = ["*"]
  }

  statement {
    sid       = "ResolveUbuntuAmi"
    actions   = ["ssm:GetParameter"]
    resources = ["arn:aws:ssm:${local.region}::parameter/aws/service/canonical/*"]
  }

  # RunInstances must be allowed on every resource type a launch touches;
  # the tag condition can only be enforced on the ones that are created and
  # tagged by the launch itself.
  statement {
    sid     = "RunTaggedInstances"
    actions = ["ec2:RunInstances"]
    resources = [
      "arn:aws:ec2:${local.region}:${data.aws_caller_identity.current.account_id}:instance/*",
      "arn:aws:ec2:${local.region}:${data.aws_caller_identity.current.account_id}:volume/*",
    ]
    condition {
      test     = "StringEquals"
      variable = "aws:RequestTag/Purpose"
      values   = ["restore-check"]
    }
  }

  statement {
    sid     = "RunInstancesSupportingResources"
    actions = ["ec2:RunInstances"]
    resources = [
      "arn:aws:ec2:${local.region}::image/*",
      "arn:aws:ec2:${local.region}:${data.aws_caller_identity.current.account_id}:network-interface/*",
      "arn:aws:ec2:${local.region}:${data.aws_caller_identity.current.account_id}:subnet/*",
      "arn:aws:ec2:${local.region}:${data.aws_caller_identity.current.account_id}:security-group/*",
    ]
  }

  statement {
    sid       = "TagOnLaunchOnly"
    actions   = ["ec2:CreateTags"]
    resources = ["arn:aws:ec2:${local.region}:${data.aws_caller_identity.current.account_id}:*/*"]
    condition {
      test     = "StringEquals"
      variable = "ec2:CreateAction"
      values   = ["RunInstances"]
    }
  }

  statement {
    sid       = "TerminateOnlyTaggedInstances"
    actions   = ["ec2:TerminateInstances"]
    resources = ["*"]
    condition {
      test     = "StringEquals"
      variable = "ec2:ResourceTag/Purpose"
      values   = ["restore-check"]
    }
  }

  # The provider sets instance_initiated_shutdown_behavior with a separate
  # ModifyInstanceAttribute call after launch, so CI may set exactly that
  # attribute, on its own tagged instances, and nothing else.
  statement {
    sid       = "ModifyOnlyTaggedInstancesShutdownBehaviour"
    actions   = ["ec2:ModifyInstanceAttribute"]
    resources = ["arn:aws:ec2:${local.region}:${data.aws_caller_identity.current.account_id}:instance/*"]
    condition {
      test     = "StringEquals"
      variable = "ec2:ResourceTag/Purpose"
      values   = ["restore-check"]
    }
    # IfExists with both documented casings: pins the attribute when EC2
    # provides the context key, and falls back to the tag fence when the
    # call shape omits it (absent key + plain StringEquals would deny).
    condition {
      test     = "StringEqualsIfExists"
      variable = "ec2:Attribute"
      values   = ["InstanceInitiatedShutdownBehavior", "instanceInitiatedShutdownBehavior"]
    }
  }

  statement {
    sid       = "TunnelThroughEndpoint"
    actions   = ["ec2-instance-connect:OpenTunnel"]
    resources = [aws_ec2_instance_connect_endpoint.restore_check.arn]
    condition {
      test     = "NumericEquals"
      variable = "ec2-instance-connect:remotePort"
      values   = ["22"]
    }
  }

  statement {
    sid       = "PushEphemeralSshKey"
    actions   = ["ec2-instance-connect:SendSSHPublicKey"]
    resources = ["arn:aws:ec2:${local.region}:${data.aws_caller_identity.current.account_id}:instance/*"]
    condition {
      test     = "StringEquals"
      variable = "ec2:osuser"
      values   = ["ubuntu"]
    }
    condition {
      test     = "StringEquals"
      variable = "aws:ResourceTag/Purpose"
      values   = ["restore-check"]
    }
  }

  statement {
    sid       = "ListRunRootState"
    actions   = ["s3:ListBucket"]
    resources = ["arn:aws:s3:::${local.state_bucket}"]
    condition {
      test     = "StringLike"
      variable = "s3:prefix"
      values   = ["restore-check/run/*"]
    }
  }

  statement {
    sid       = "ReadWriteRunRootState"
    actions   = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"]
    resources = ["arn:aws:s3:::${local.state_bucket}/restore-check/run/*"]
  }
}

# Set these as GitHub Actions repository variables for the workflow:
# RESTORE_CHECK_EICE_ID, RESTORE_CHECK_SUBNET_ID and
# RESTORE_CHECK_INSTANCE_SG_ID respectively.
output "eice_id" {
  value = aws_ec2_instance_connect_endpoint.restore_check.id
}

output "subnet_id" {
  value = local.subnet_id
}

output "instance_security_group_id" {
  value = aws_security_group.instance.id
}
