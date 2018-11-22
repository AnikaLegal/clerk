# Clerk

This site is used by new Anika clients who want to submit their legal problem. Clients may submit the facts of their case using a structured form interface. Their case file is then entered into our case managment system.

This is a speculative project built out for Random Hacks of Kindness (Melbourne, Summer 2018).

> Depending on the job, office clerks might answer phones, filing, data processing, faxing, envelope stuffing and mailing, message delivery, running errands, sorting incoming mail and much more. ([source](https://www.snagajob.com/job-descriptions/office-clerk/))


# Development

## Prerequisites

You will need:

- `docker` ([install here](https://docs.docker.com/install/#supported-platforms))
- `docker-compose` ([install here](https://docs.docker.com/compose/install/))

For Ubuntu the install looks something like this:

```bash
sudo -i
apt update
apt install \
    apt-transport-https \
    ca-certificates \
    curl \
    software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"
apt update
apt install docker-ce

curl -L \
    "https://github.com/docker/compose/releases/download/1.23.1/docker-compose-$(uname -s)-$(uname -m)" \
    -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

docker run hello-world
```
## Getting Started

You first want to "build" the Docker image that we'll be using. This Docker image is based on the `ubuntu:bionic` base image, with the addition of Python 3 and NodeJS,  installed using `Dockerfile.base`. The Ubuntu + Python 3 + NodeJS image has been uploaded to Docker Hub as `anikalaw/clerkbase` ([here](https://hub.docker.com/r/anikalaw/clerkbase/).

To build your local Docker image:

```bash
# This will download the ~300MB anikalaw/clerkbase image and add some extra stuff.
docker-compose build
```

This will run the `Dockerfile` and install any required Python and NodeJS packages. To run the webserver:

```bash
# Setup the development database for Django
docker-compose run web ./manage.py migrate

# Bring up development containers - will show Django dev server logs
docker-compose up web

# In another console window/tab, run this to see webpack output
docker-compose logs -f --tail 100 webpack
```
