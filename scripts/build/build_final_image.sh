#/bin/bash
set -e

# Build final docker image and push it to Docker Hub
DOCKER_ID='anikalaw'
IMAGE_NAME='clerk'
DOCKERFILE='docker/Dockerfile'

cat ~/.dockercreds | docker login --username $DOCKER_ID --password-stdin
docker build -t $DOCKER_ID/$IMAGE_NAME:latest -f $DOCKERFILE .
docker push $DOCKER_ID/$IMAGE_NAME
