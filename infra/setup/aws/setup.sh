#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

# AWS CLI version to install, pinned so that a rebuilt host matches the
# current one. Available versions are listed in the AWS CLI changelog:
# https://raw.githubusercontent.com/aws/aws-cli/v2/CHANGELOG.rst
# See docs/infra.md.
AWS_CLI_VERSION="2.34.0"

echo -e "\n>>> Installing AWS CLI $AWS_CLI_VERSION"

# Prevent locale warnings during installation
export LC_ALL=C.UTF-8
export DEBIAN_FRONTEND=noninteractive
# Restart services automatically instead of prompting (needrestart)
export NEEDRESTART_MODE=a

apt-get install --yes curl unzip

# uname -m gives x86_64 or aarch64, matching the AWS CLI download names.
ARCH=$(uname -m)
curl -fsSL "https://awscli.amazonaws.com/awscli-exe-linux-${ARCH}-${AWS_CLI_VERSION}.zip" -o "/tmp/awscliv2.zip"
unzip -q -d /tmp /tmp/awscliv2.zip
/tmp/aws/install --update
aws --version

rm /tmp/awscliv2.zip
rm -rf /tmp/aws

echo -e "\n>>> Finished installing AWS CLI"
