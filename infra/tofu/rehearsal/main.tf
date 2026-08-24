# The throwaway host for the bi-annual restore rehearsal (TEC-2044): a
# blank server the drill rebuilds from scratch with the infra/setup
# scripts, restores both databases onto, verifies, and destroys the same
# day. Applied and destroyed per drill via the `rehearsal` just module
# (infra/rehearsal/justfile); between drills this root holds nothing.
#
#   just rehearsal up      # apply (detects your IP, installs your SSH key)
#   just rehearsal down    # destroy + tag sweep
#
# Safety posture: the host lives in its own throwaway VPC (nothing
# shared with the live server's network), SSH from the operator's IP
# only, nothing else inbound; real production data lands on this host
# during the drill, so user-data arms a self-destruct - the instance
# terminates itself after self_destruct_minutes even if the operator
# walks away. A drill that legitimately needs longer can disarm and
# re-arm it (see docs/restore-check.md).

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

variable "ssh_public_keys" {
  description = "The operator's SSH public key(s), one per line, installed for root"
  type        = string
  default     = ""
}

variable "self_destruct_minutes" {
  description = "The instance terminates itself after this long, drill finished or not"
  type        = number
  default     = 240
}

# The drill's own throwaway network: the host carries real production
# data, so it shares nothing with the live server's VPC - and the Sentry
# blackhole zone below can attach here with a blast radius of exactly
# this drill. DNS support and hostnames must both be on for a private
# hosted zone to resolve.
resource "aws_vpc" "rehearsal" {
  cidr_block           = "10.66.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "rehearsal"
  }
}

resource "aws_subnet" "rehearsal" {
  vpc_id     = aws_vpc.rehearsal.id
  cidr_block = "10.66.0.0/24"

  tags = {
    Name = "rehearsal"
  }
}

resource "aws_internet_gateway" "rehearsal" {
  vpc_id = aws_vpc.rehearsal.id

  tags = {
    Name = "rehearsal"
  }
}

resource "aws_route_table" "rehearsal" {
  vpc_id = aws_vpc.rehearsal.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.rehearsal.id
  }

  tags = {
    Name = "rehearsal"
  }
}

resource "aws_route_table_association" "rehearsal" {
  subnet_id      = aws_subnet.rehearsal.id
  route_table_id = aws_route_table.rehearsal.id
}

# The latest Canonical Ubuntu 24.04 AMI, resolved through AWS' public SSM
# parameter at each apply.
data "aws_ssm_parameter" "ubuntu_noble_ami" {
  name = "/aws/service/canonical/ubuntu/server/24.04/stable/current/amd64/hvm/ebs-gp3/ami-id"
}

resource "aws_security_group" "rehearsal" {
  name        = "rehearsal-host"
  description = "Rehearsal host: SSH from the operator only"
  vpc_id      = aws_vpc.rehearsal.id
}

resource "aws_vpc_security_group_ingress_rule" "rehearsal_ssh" {
  security_group_id = aws_security_group.rehearsal.id
  description       = "SSH from the operator IP only"
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
  subnet_id              = aws_subnet.rehearsal.id
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
    ssh_public_keys       = var.ssh_public_keys
    self_destruct_minutes = var.self_destruct_minutes
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

# Sentry blackhole: the drill stack uses the real staging Sentry DSN, so
# resolve sentry.io (apex and every subdomain) to loopback for the drill
# VPC's resolver, which the containers' DNS goes through. Attach only to
# the drill's own VPC - on a shared VPC this would also silence the
# production host's error reporting.
resource "aws_route53_zone" "sentry_blackhole" {
  name    = "sentry.io"
  comment = "Rehearsal drill Sentry blackhole - exists only while a drill host does"

  vpc {
    vpc_id = aws_vpc.rehearsal.id
  }
}

resource "aws_route53_record" "sentry_apex" {
  zone_id = aws_route53_zone.sentry_blackhole.zone_id
  name    = "sentry.io"
  type    = "A"
  ttl     = 60
  records = ["127.0.0.1"]
}

resource "aws_route53_record" "sentry_wildcard" {
  zone_id = aws_route53_zone.sentry_blackhole.zone_id
  name    = "*.sentry.io"
  type    = "A"
  ttl     = 60
  records = ["127.0.0.1"]
}

output "public_ip" {
  value = aws_instance.rehearsal.public_ip
}

output "instance_id" {
  value = aws_instance.rehearsal.id
}
