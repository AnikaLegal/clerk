#!/bin/bash
set -e
echo -e "\n>>> Hardening server"

# Patch all software
apt-get update -qq
apt-get upgrade --yes

# Disable SSH password based login
sed -i "s/PasswordAuthentication yes/PasswordAuthentication no/" /etc/ssh/sshd_config
systemctl restart sshd

# Enable firewall
ufw default allow outgoing
ufw default deny incoming
ufw allow 22
ufw allow 80
ufw enable
ufw status

# TODO: Enable unattended upgrades (not sure best way to do)
# apt-get install unattended-upgrades
# dpkg-reconfigure -f noninteractive unattended-upgrades

# TODO: Fail2ban

echo -e "\n>>> Finished hardening server"
