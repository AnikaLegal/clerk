#!/usr/bin/env bash
set -o errexit

if ! command -v docker &> /dev/null
then
    echo -e "\n>>> Installing Docker"

    # Prevent locale warnings during installation
    export LC_ALL=C.UTF-8
    export DEBIAN_FRONTEND=noninteractive

    # Add Docker's official GPG key:
    apt-get update
    apt-get install --yes ca-certificates curl
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    chmod a+r /etc/apt/keyrings/docker.asc

    # Add the repository to Apt sources:
    tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Signed-By: /etc/apt/keyrings/docker.asc
EOF

    apt-get install --yes docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    echo -e "\n>>> Enabling Docker Swarm"
    docker swarm init
else
    echo -e "\n>>> Docker already installed"
fi
