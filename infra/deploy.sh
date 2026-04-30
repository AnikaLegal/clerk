#!/bin/bash
#
# Deploy clerk the host server
# Run this from the project root
#
set -o errexit
set -o pipefail

if [[ -z "$COMPOSE_SUFFIX" ]]; then
    echo -e "\n>>> Error: Docker Compose suffix not found in COMPOSE_SUFFIX"
    exit 1
fi
if [[ -z "$CLERK_PRIVATE_SSH_KEY" ]]; then
    echo -e "\n>>> Error: Clerk private key not found in CLERK_PRIVATE_SSH_KEY"
    exit 1
fi

CLERK_HOST=$(grep "^CLERK_HOST=" env/${COMPOSE_SUFFIX}.env | cut -d '=' -f2-)
if [[ -z "$CLERK_HOST" ]]; then
    echo -e "\n>>> Error: CLERK_HOST not found in env/${COMPOSE_SUFFIX}.env"
    exit 1
fi

PROJECT_NAME="clerk_$COMPOSE_SUFFIX"

echo -e "\n>>> Deploying $PROJECT_NAME to host $CLERK_HOST"

echo -e "\n>>> Setting up SSH"
mkdir ~/.ssh
echo -e "$CLERK_PRIVATE_SSH_KEY" >~/.ssh/id_ed25519
chmod 600 ~/.ssh/id_ed25519
cat >> ~/.ssh/config <<END
Host $CLERK_HOST
  StrictHostKeyChecking no
END

echo -e "\n>>> Setting up Docker context"
docker context create remote --docker "host=ssh://root@${CLERK_HOST}"
docker context use remote

echo -e "\n>>> Deploying $PROJECT_NAME to Docker Swarm cluster on host $CLERK_HOST"
docker stack deploy --compose-file "docker/docker-compose.${COMPOSE_SUFFIX}.yml" $PROJECT_NAME

echo -e "\n>>> Removing unused Docker objects (containers, images, volumes, networks, build cache)"
docker system prune --all --volumes --force

echo -e "\n>>> Deployment finished for $PROJECT_NAME"
