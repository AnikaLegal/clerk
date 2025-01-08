#!/bin/bash
#
# Deploy clerk the host server
# Run this from the project root
#
set -o errexit
set -o pipefail

HOST='13.55.250.149'

if [[ -z "$COMPOSE_SUFFIX" ]]; then
    echo -e "\n>>> Error: Docker Compose suffix not found in COMPOSE_SUFFIX"
    exit 1
fi
if [[ -z "$PROJECT" ]]; then
    echo -e "\n>>> Error: Project name not found in PROJECT"
    exit 1
fi
if [[ -z "$CLERK_PRIVATE_SSH_KEY" ]]; then
    echo -e "\n>>> Error: Clerk private key not found in CLERK_PRIVATE_SSH_KEY"
    exit 1
fi

echo -e "\n>>> Deploying $PROJECT to host $HOST with suffix $COMPOSE_SUFFIX"

echo -e "\n>>> Setting up SSH"
mkdir ~/.ssh
echo -e "$CLERK_PRIVATE_SSH_KEY" >~/.ssh/id_ed25519
chmod 600 ~/.ssh/id_ed25519
cat >> ~/.ssh/config <<END
Host $HOST
  StrictHostKeyChecking no
END

echo -e "\n>>> Setting up Docker context"
docker context create remote --docker "host=ssh://root@${HOST}"
docker context use remote

echo -e "\n>>> Deploying $PROJECT to Docker Swarm cluster on host $HOST"
docker stack deploy --compose-file "docker/docker-compose.${COMPOSE_SUFFIX}.yml" $PROJECT

echo -e "\n>>> Removing unused Docker objects (containers, images, volumes, networks, build cache)"
docker system prune --volumes --force

echo -e "\n>>> Deployment finished for $PROJECT"
