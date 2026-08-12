# The throwaway host for the bi-annual restore rehearsal (TEC-2044): a
# blank server the drill rebuilds from scratch with the infra/setup
# scripts, restores both databases onto, verifies, and destroys the same
# day. Applied and destroyed per drill via the `rehearsal` just module
# (infra/rehearsal/justfile); between drills this root holds nothing.
#
#   just rehearsal up      # apply (detects your IP, installs your SSH key)
#   just rehearsal down    # destroy + tag sweep
#
# Safety posture: SSH from the operator's IP only, nothing else inbound;
# real production data lands on this host during the drill, so user-data
# arms a self-destruct - the instance terminates itself after
# self_destruct_minutes even if the operator walks away. A drill that
# legitimately needs longer can disarm and re-arm it (see
# docs/restore-check.md).

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
    key          = "rehearsal/terraform.tfstate"
    region       = "ap-southeast-2"
    use_lockfile = true
  }
}

provider "aws" {
  region = "ap-southeast-2"

  default_tags {
    tags = {
      Purpose = "rehearsal"
    }
  }
}

# Defaults exist so `tofu destroy` needs no variables; `up` always passes
# real values.
variable "operator_ip" {
  description = "The operator's public IP: the only address allowed to SSH in"
  type        = string
  default     = "127.0.0.1"
}

variable "ssh_public_key" {
  description = "The operator's SSH public key, installed for root"
  type        = string
  default     = ""
}

variable "self_destruct_minutes" {
  description = "The instance terminates itself after this long, drill finished or not"
  type        = number
  default     = 240
}

data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# The latest Canonical Ubuntu 24.04 AMI, resolved through AWS' public SSM
# parameter at each apply.
data "aws_ssm_parameter" "ubuntu_noble_ami" {
  name = "/aws/service/canonical/ubuntu/server/24.04/stable/current/amd64/hvm/ebs-gp3/ami-id"
}

resource "aws_security_group" "rehearsal" {
  name        = "rehearsal-host"
  description = "Rehearsal host: SSH from the operator only"
  vpc_id      = data.aws_vpc.default.id
}

resource "aws_vpc_security_group_ingress_rule" "rehearsal_ssh" {
  security_group_id = aws_security_group.rehearsal.id
  description       = "SSH from the operator's IP"
  ip_protocol       = "tcp"
  from_port         = 22
  to_port           = 22
  cidr_ipv4         = "${var.operator_ip}/32"
}

resource "aws_vpc_security_group_egress_rule" "rehearsal_all_out" {
  security_group_id = aws_security_group.rehearsal.id
  ip_protocol       = "-1"
  cidr_ipv4         = "0.0.0.0/0"
}

resource "aws_instance" "rehearsal" {
  ami                    = data.aws_ssm_parameter.ubuntu_noble_ami.value
  instance_type          = "t3.small"
  subnet_id              = sort(data.aws_subnets.default.ids)[0]
  vpc_security_group_ids = [aws_security_group.rehearsal.id]

  # A public address: SSH in from the operator, apt/S3/Docker Hub out.
  associate_public_ip_address = true

  # The self-destruct in user-data ends in a halt; this turns that halt
  # into termination, so the failsafe really removes the host.
  instance_initiated_shutdown_behavior = "terminate"

  # Never update user-data on a live instance: the AWS API does that via
  # stop/start, which would wipe the armed self-destruct without ever
  # re-running cloud-init to re-arm it. A changed rendering must mean a
  # fresh host.
  user_data_replace_on_change = true

  user_data = templatefile("${path.module}/user-data.yml.tftpl", {
    ssh_public_key        = var.ssh_public_key
    self_destruct_minutes = var.self_destruct_minutes
    # Every hostname the clerk Sentry DSNs point at, blackholed in
    # /etc/hosts so the drill's staging stack cannot leak errors into the
    # real staging Sentry project (it shares the DSN; only the environment
    # tag differs). /etc/hosts matches exact names only, so each host the
    # env files reference is listed: the backend RAVEN_DSN targets plain
    # sentry.io, the SENTRY_JS_DSN targets the org ingest host, and the
    # modern .us form is included for when the DSNs are next rotated.
    # (Browser-side JS events from anyone viewing the drill site originate
    # off-host and cannot be blocked here - only the operator ever loads
    # it, so that residue is accepted.)
    sentry_hosts = [
      "sentry.io",
      "o264950.ingest.sentry.io",
      "o264950.ingest.us.sentry.io",
    ]
  })

  # Room for the restored databases plus the Docker images.
  root_block_device {
    volume_size = 20
    volume_type = "gp3"
  }

  tags = {
    Name = "rehearsal"
  }

  # Volumes do not inherit provider default_tags; tag explicitly so the
  # teardown sweep sees them.
  volume_tags = {
    Name    = "rehearsal"
    Purpose = "rehearsal"
  }
}

output "public_ip" {
  value = aws_instance.rehearsal.public_ip
}

output "instance_id" {
  value = aws_instance.rehearsal.id
}
