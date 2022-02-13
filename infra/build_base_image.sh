#/bin/bash
set -e

if [ -z "$DOCKER_PASSWORD" ]
then
    echo "DOCKER_PASSWORD not set."
    exit 1
fi

# Build base docker image and push it to Docker Hub
DOCKER_ID='anikalaw'
IMAGE_NAME='clerkbase'
DOCKERFILE='docker/Dockerfile.base'

docker login --username $DOCKER_ID --password $DOCKER_PASSWORD
docker build --no-cache -t $DOCKER_ID/$IMAGE_NAME:latest -f $DOCKERFILE .
docker push $DOCKER_ID/$IMAGE_NAME
