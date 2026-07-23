#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

# PostgreSQL major version to install. Must match the postgresql-client
# version in docker/Dockerfile.base so that backups taken with pg_dump can be
# restored to this server. See docs/infra.md.
POSTGRES_VERSION=16

echo -e "\n>>> Installing Postgres $POSTGRES_VERSION"
export DEBIAN_FRONTEND=noninteractive
# Restart services automatically instead of prompting (needrestart)
export NEEDRESTART_MODE=a

# Install from the PGDG apt repository pinned to a specific major version,
# rather than whatever version Ubuntu happens to ship.
apt-get install --yes curl ca-certificates

# Add PGDG's official GPG key:
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc -o /etc/apt/keyrings/pgdg.asc
chmod a+r /etc/apt/keyrings/pgdg.asc

# Add the repository to Apt sources:
tee /etc/apt/sources.list.d/pgdg.sources <<EOF
Types: deb
URIs: https://apt.postgresql.org/pub/repos/apt
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")-pgdg
Components: main
Signed-By: /etc/apt/keyrings/pgdg.asc
EOF

apt-get update -qq

# NOTE: install the versioned package only. The unversioned "postgresql" and
# "postgresql-contrib" metapackages would pull in PGDG's current default
# version, which defeats the pin. Contrib modules are included in the server
# package since PostgreSQL 14.
apt-get install --yes postgresql-$POSTGRES_VERSION

echo -e "\n>>> Updating Postgres config"

# Listen on all interfaces for Retool access. Use a conf.d drop-in file
# rather than editing postgresql.conf in place, so that re-running this
# script is idempotent. The stock postgresql.conf includes conf.d by default.
CONF_DIR="/etc/postgresql/$POSTGRES_VERSION/main/conf.d"
cp /srv/infra/postgres/clerk.conf $CONF_DIR/clerk.conf
chmod 644 $CONF_DIR/clerk.conf

# Use our custom pg_hba.conf to allow access to Retool IPs. See
# https://docs.retool.com/data-sources/guides/connect/postgresql
HBA_FILE=$(sudo -u postgres psql -tAc 'SHOW hba_file;')
cp /srv/infra/postgres/pg_hba.conf $HBA_FILE
chmod 644 $HBA_FILE

echo -e "\n>>> Restarting Postgres"
systemctl restart postgresql

echo -e "\n>>> Finished installing Postgres"