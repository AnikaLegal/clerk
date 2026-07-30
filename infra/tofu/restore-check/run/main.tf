# The ephemeral restore check instance (TEC-1987). Applied and destroyed by
# CI on every monthly run (see infra/restore-check/run.sh); nothing here is
# long-lived. The standing resources it plugs into - the subnet, the
# instance security group and the Instance Connect Endpoint - are defined in
# ../foundations and passed in as variables by the workflow.

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
    key          = "restore-check/run/terraform.tfstate"
    region       = "ap-southeast-2"
    use_lockfile = true
  }
}

provider "aws" {
  region = "ap-southeast-2"

  # The CI user's TerminateInstances permission is gated on this tag.
  default_tags {
    tags = {
      Purpose = "restore-check"
    }
  }
}

variable "subnet_id" {
  description = "Subnet to launch into: must be the Instance Connect Endpoint's subnet (foundations output subnet_id)"
  type        = string
}

variable "instance_security_group_id" {
  description = "The standing instance security group: SSH from the endpoint only (foundations output instance_security_group_id)"
  type        = string
}

# The latest Canonical Ubuntu 24.04 AMI, resolved through AWS' public SSM
# parameter at each run.
data "aws_ssm_parameter" "ubuntu_noble_ami" {
  name = "/aws/service/canonical/ubuntu/server/24.04/stable/current/amd64/hvm/ebs-gp3/ami-id"
}

resource "aws_instance" "restore_check" {
  ami                    = data.aws_ssm_parameter.ubuntu_noble_ami.value
  instance_type          = "t3.small"
  subnet_id              = var.subnet_id
  vpc_security_group_ids = [var.instance_security_group_id]

  # A public address for outbound traffic only (apt, S3); the security
  # group accepts nothing from the internet.
  associate_public_ip_address = true

  # The failsafe shutdown scheduled in user-data destroys the instance even
  # if the runner dies before its tofu destroy runs.
  instance_initiated_shutdown_behavior = "terminate"

  user_data = file("${path.module}/user-data.sh")

  tags = {
    Name = "restore-check"
  }

  volume_tags = {
    Purpose = "restore-check"
  }
}

output "instance_id" {
  value = aws_instance.restore_check.id
}
