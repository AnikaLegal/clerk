#!/bin/bash
# Bootstrap for the restore check instance: install the pinned Postgres
# major (must match the server pin, see infra/setup/postgres/setup.sh and
# docs/infra.md) plus the tools check.py needs. ec2-instance-connect serves
# the per-run SSH key pushed by run.sh; Ubuntu AMIs preinstall it, but it is
# listed anyway to be explicit. Contains no secrets: user data is readable
# via the EC2 API and stored in OpenTofu state.
set -e
export DEBIAN_FRONTEND=noninteractive

# Arm the failsafe before anything that can fail: with shutdown behaviour
# "terminate" the instance destroys itself within the hour even if the
# runner dies or this script aborts partway.
shutdown -h +60

install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc -o /etc/apt/keyrings/pgdg.asc
echo "deb [signed-by=/etc/apt/keyrings/pgdg.asc] https://apt.postgresql.org/pub/repos/apt noble-pgdg main" > /etc/apt/sources.list.d/pgdg.list
apt-get update -qq
apt-get install --yes -qq postgresql-16 ec2-instance-connect unzip

# Ubuntu 24.04 no longer packages awscli in its archive; install the same
# pinned AWS CLI v2 as the server (see infra/setup/aws/setup.sh).
curl -fsSL "https://awscli.amazonaws.com/awscli-exe-linux-$(uname -m)-2.34.0.zip" -o /tmp/awscliv2.zip
unzip -q -d /tmp /tmp/awscliv2.zip
/tmp/aws/install

sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'restore-check';"
touch /var/tmp/restore-check-ready
