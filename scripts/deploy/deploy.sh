#!/bin/bash
#
# Deploy clerk the host server
# Run this from the project root
#
set -e
HOST='3.106.55.74'

if [[ -z "$COMPOSE_SUFFIX" ]]
then
    echo -e "\n>>> Error: Docker Compose suffix not found in COMPOSE_SUFFIX."
    exit 1
fi

if [[ -z "$PROJECT" ]]
then
    echo -e "\n>>> Error: Project name not found in PROJECT."
    exit 1
fi

if [[ -z "$CLERK_PRIVATE_SSH_KEY" ]]
then
    echo -e "\n>>> Error: Clerk private key not found in CLERK_PRIVATE_SSH_KEY."
    exit 1
fi

echo -e "\n>>> Deploying $PROJECT to clerk at $HOST with suffix $COMPOSE_SUFFIX."

# Set up SSH key
echo -e "\n>>> Setting up private key."
echo -e "$CLERK_PRIVATE_SSH_KEY" > deploy.key
chmod 600 deploy.key

echo -e "\n>>> SSHing into clerk at $HOST."
ssh -v -i deploy.key root@$HOST /bin/bash << EOF
    set -e
    echo -e "\n>>> Setting up deployment files for $PROJECT"
    mkdir -p /srv/${PROJECT}/
EOF

echo -e "\n>>> Copying $PROJECT compose file to clerk at $HOST"
scp docker/docker-compose.${COMPOSE_SUFFIX}.yml root@${HOST}:/srv/$PROJECT

echo -e "\n>>> SSHing into clerk at $HOST."
ssh -v -i deploy.key root@$HOST /bin/bash << EOF
    set -e
    echo -e "\n>>> Deploying $PROJECT to Docker Swarm cluster"
    docker stack deploy \
        --compose-file /srv/${PROJECT}/docker-compose.${COMPOSE_SUFFIX}.yml \
        $PROJECT
EOF
echo -e "\n>>> Deployment finished for $PROJECT"
