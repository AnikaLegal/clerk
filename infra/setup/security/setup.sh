#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

echo -e "\n>>> Hardening server"

# Prevent locale warnings during installation
export LC_ALL=C.UTF-8
export DEBIAN_FRONTEND=noninteractive
# Restart services automatically instead of prompting (needrestart)
export NEEDRESTART_MODE=a

# Patch all software
echo -e "\n>>> Updating and patching software"
apt-get update -qq
# Keep existing config files when packages ship new defaults, so the upgrade
# can never stop on a dpkg conffile prompt.
apt-get upgrade --yes \
    -o Dpkg::Options::="--force-confdef" \
    -o Dpkg::Options::="--force-confold"

# Disable password authentication
echo -e "\n>>> Disabling password authentication for SSH"
cp /srv/infra/security/99-disable-password-auth.conf /etc/ssh/sshd_config.d/
systemctl restart ssh

# Unattended upgrades default to 06:00-07:00 UTC, mid-afternoon in Melbourne,
# and needrestart then restarts Postgres, NGINX and containerd. Run them at
# 18:00 UTC instead, a quiet hour that is clear of the nightly backup.
echo -e "\n>>> Scheduling unattended upgrades for 18:00 UTC"
mkdir -p /etc/systemd/system/apt-daily-upgrade.timer.d
cp /srv/infra/security/apt-daily-upgrade-override.conf /etc/systemd/system/apt-daily-upgrade.timer.d/override.conf
systemctl daemon-reload
# A running timer only picks up a new schedule when restarted.
systemctl restart apt-daily-upgrade.timer

echo -e "\n>>> Finished hardening server"
