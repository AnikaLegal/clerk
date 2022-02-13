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
DEPLOY_DIR="/srv/deploy/${PROJECT}/$(date +%s)"

ssh -o StrictHostKeyChecking=no -i deploy.key root@$HOST /bin/bash << EOF
    set -e
    echo -e "\n>>> Setting up deployment files for $PROJECT at $DEPLOY_DIR"
    mkdir -p $DEPLOY_DIR
EOF

echo -e "\n>>> Copying $PROJECT files to clerk at $HOST"
scp -o StrictHostKeyChecking=no -i deploy.key docker/docker-compose.${COMPOSE_SUFFIX}.yml root@${HOST}:$DEPLOY_DIR
scp -o StrictHostKeyChecking=no -i deploy.key env/${COMPOSE_SUFFIX}.env root@${HOST}:$DEPLOY_DIR

echo -e "\n>>> SSHing into clerk at $HOST."
ssh -o StrictHostKeyChecking=no -i deploy.key root@$HOST /bin/bash << EOF
    set -e
    cd $DEPLOY_DIR
    echo -e "\n>>> Deploying $PROJECT to Docker Swarm cluster from $DEPLOY_DIR"
    docker stack deploy --compose-file docker-compose.${COMPOSE_SUFFIX}.yml $PROJECT
EOF
echo -e "\n>>> Deployment finished for $PROJECT"
