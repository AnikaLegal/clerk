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

echo -e "\n>>> Finished hardening server"
