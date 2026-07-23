#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

# Docker package versions to install, pinned so that a rebuilt host matches
# the current one. These version strings are specific to the host's Ubuntu
# release: list the available versions with `apt-cache madison docker-ce`.
# See docs/infra.md.
DOCKER_VERSION="5:29.2.1-1~ubuntu.24.04~noble"
CONTAINERD_VERSION="2.2.1-1~ubuntu.24.04~noble"
BUILDX_VERSION="0.31.1-1~ubuntu.24.04~noble"
COMPOSE_VERSION="5.1.0-1~ubuntu.24.04~noble"

if ! command -v docker &> /dev/null
then
    echo -e "\n>>> Installing Docker"

    # Prevent locale warnings during installation
    export LC_ALL=C.UTF-8
    export DEBIAN_FRONTEND=noninteractive
    # Restart services automatically instead of prompting (needrestart)
    export NEEDRESTART_MODE=a

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

    apt-get update
    apt-get install --yes \
        docker-ce=$DOCKER_VERSION \
        docker-ce-cli=$DOCKER_VERSION \
        docker-ce-rootless-extras=$DOCKER_VERSION \
        containerd.io=$CONTAINERD_VERSION \
        docker-buildx-plugin=$BUILDX_VERSION \
        docker-compose-plugin=$COMPOSE_VERSION
else
    echo -e "\n>>> Docker already installed"
fi

# Hold the pinned packages so apt-get upgrade (run by security/setup.sh and
# any later manual patching) cannot walk them off the pinned versions. To
# upgrade Docker deliberately: bump the versions above, apt-mark unhold the
# packages, and re-run the install.
apt-mark hold \
    docker-ce \
    docker-ce-cli \
    docker-ce-rootless-extras \
    containerd.io \
    docker-buildx-plugin \
    docker-compose-plugin

# Swarm is guarded separately from the Docker install, so that a host where
# Docker is installed but Swarm was never enabled still gets initialised.
if [ "$(docker info --format '{{.Swarm.LocalNodeState}}')" = "active" ]; then
    echo -e "\n>>> Docker Swarm already enabled"
else
    echo -e "\n>>> Enabling Docker Swarm"
    # Make the advertise address explicit: swarm init cannot autodetect it on
    # hosts with more than one network interface.
    docker swarm init --advertise-addr "$(hostname -I | awk '{print $1}')"
fi
