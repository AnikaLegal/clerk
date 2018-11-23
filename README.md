# Clerk

This site is used by new Anika clients who want to submit their legal problem. Clients may submit the facts of their case using a structured form interface. Their case file is then entered into our case managment system.

This is a speculative project built out for Random Hacks of Kindness (Melbourne, Summer 2018).

> Depending on the job, office clerks might answer phones, filing, data processing, faxing, envelope stuffing and mailing, message delivery, running errands, sorting incoming mail and much more. ([source](https://www.snagajob.com/job-descriptions/office-clerk/))

[![CircleCI](https://circleci.com/gh/AnikaLegal/clerk.svg?style=svg)](https://circleci.com/gh/AnikaLegal/clerk)

# Development

## Prerequisites

You will need:

- `docker` ([install](https://docs.docker.com/install/#supported-platforms))
- `docker-compose` ([install](https://docs.docker.com/compose/install/))

For Ubuntu, the install looks something like this:

```bash
# Become root
sudo -i
# Install Docker prequisites
apt update
apt install \
    apt-transport-https \
    ca-certificates \
    curl \
    software-properties-common

# Add docker repository to apt
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"

# Install Docker
apt update
apt install docker-ce

# Download docker-compose binary
curl -L \
    "https://github.com/docker/compose/releases/download/1.23.1/docker-compose-$(uname -s)-$(uname -m)" \
    -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Verify that Docker works
docker run hello-world

# Verify that Docker Compose works
docker-compose version
```
## Getting Started

You first want to build the Docker image that we'll be using. This Docker image is based on the [`ubuntu:bionic`](https://hub.docker.com/_/ubuntu/) base image, with the addition of Python 3 and NodeJS, which are installed in [`Dockerfile.base`](./Dockerfile.base). The Ubuntu + Python 3 + NodeJS image has been uploaded to Docker Hub as  [`anikalaw/clerkbase`](https://hub.docker.com/r/anikalaw/clerkbase/).

To build your local Docker image:

```bash
# This will download the ~300MB anikalaw/clerkbase image and add some extra stuff.
docker-compose build
```

The build step will run the steps in [`Dockerfile`](./Dockerfile) and install any required Python and NodeJS libraries. To run the development environment:

```bash
# Setup the development database for Django
docker-compose run web ./manage.py migrate

# Bring up development containers - will show Django dev server logs
docker-compose up web

# In another console window/tab, run this to see webpack output
docker-compose run --service-ports webpack
```

Now you should be able to visit [`http://localhost:8000`](http://localhost:8000) and see the Clerk site.
