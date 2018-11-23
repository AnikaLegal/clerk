#/bin/bash
# Build the docker image if we do not have a pre-built image
# Otherwise we can use the pre-built image
set -e
if [ -f "image.tar" ]
then
    echo "Using cached version of anikalaw/clerk"
else
    echo "Building anikalaw/clerk"
    docker build -t anikalaw/clerk .
    echo "Saving anikalaw/clerk"
    docker save -o image.tar anikalaw/clerk
fi
