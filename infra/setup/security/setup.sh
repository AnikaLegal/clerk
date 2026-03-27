#!/usr/bin/env bash
set -o errexit

echo -e "\n>>> Hardening server"

# Prevent locale warnings during installation
export LC_ALL=C.UTF-8
export DEBIAN_FRONTEND=noninteractive

# Patch all software
echo -e "\n>>> Updating and patching software"
apt-get update -qq
apt-get upgrade --yes

# Disable password authentication
echo -e "\n>>> Disabling password authentication for SSH"
cp /srv/infra/security/99-disable-password-auth.conf /etc/ssh/sshd_config.d/
systemctl restart ssh

echo -e "\n>>> Finished hardening server"
