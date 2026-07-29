#!/bin/bash
# Bootstrap for the restore check instance: install the pinned Postgres
# major (must match the server pin, see infra/setup/postgres/setup.sh and
# docs/infra.md) plus the tools check.py needs. ec2-instance-connect serves
# the per-run SSH key pushed by run.sh; Ubuntu AMIs preinstall it, but it is
# listed anyway to be explicit. The scheduled shutdown is a failsafe: with
# shutdown behaviour "terminate" the instance destroys itself even if the
# runner dies before its tofu destroy runs. Contains no secrets: user data
# is readable via the EC2 API and stored in OpenTofu state.
set -e
export DEBIAN_FRONTEND=noninteractive
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc -o /etc/apt/keyrings/pgdg.asc
echo "deb [signed-by=/etc/apt/keyrings/pgdg.asc] https://apt.postgresql.org/pub/repos/apt noble-pgdg main" > /etc/apt/sources.list.d/pgdg.list
apt-get update -qq
apt-get install --yes -qq postgresql-16 awscli ec2-instance-connect
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'restore-check';"
shutdown -h +60
touch /var/tmp/restore-check-ready
