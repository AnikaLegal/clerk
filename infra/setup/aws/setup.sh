#!/usr/bin/env bash
set -o errexit

echo -e "\n>>> Installing AWS CLI"

# Prevent locale warnings during installation
export LC_ALL=C.UTF-8
export DEBIAN_FRONTEND=noninteractive

apt-get install --yes curl unzip

curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "/tmp/awscliv2.zip"
unzip -q -d /tmp /tmp/awscliv2.zip
/tmp/aws/install --update
aws --version

rm /tmp/awscliv2.zip
rm -rf /tmp/aws

echo -e "\n>>> Finished installing AWS CLI"
