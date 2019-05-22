# Clerk

This site is used by new Anika clients who want to submit their legal problem. Clients may submit the facts of their case using a structured form interface. Their case file is then entered into our case managment system.

This is a speculative project built out for Random Hacks of Kindness (Melbourne, Summer 2018).

> Depending on the job, office clerks might answer phones, filing, data processing, faxing, envelope stuffing and mailing, message delivery, running errands, sorting incoming mail and much more. ([source](https://www.snagajob.com/job-descriptions/office-clerk/))

[![CircleCI](https://circleci.com/gh/AnikaLegal/clerk.svg?style=svg)](https://circleci.com/gh/AnikaLegal/clerk)

# TODO

- add database backup script
- add file backup script
- add S3 file storage backend
- deploy to Anika AWS

# Development

## Prerequisites

You will need:

- `docker` ([install](https://docs.docker.com/install/#supported-platforms))
- `docker-compose` ([install](https://docs.docker.com/compose/install/))

## Getting Started

You first want to build the Docker image that we'll be using. This Docker image is based on the [`ubuntu:bionic`](https://hub.docker.com/_/ubuntu/) base image, with the addition of Python 3 and NodeJS, which are installed in [`Dockerfile.base`](./Dockerfile.base). The Ubuntu + Python 3 + NodeJS image has been uploaded to Docker Hub as [`anikalaw/clerkbase`](https://hub.docker.com/r/anikalaw/clerkbase/).

To build your local Docker image:

```bash
# This will download the ~300MB anikalaw/clerkbase image.
sudo docker-compose build
```

In addition to pulling down the `clerkbase` image, the `build` step will also run the steps in [`Dockerfile`](./Dockerfile) and install any required Python and NodeJS libraries. After this is done, you can start the development environment:

```bash
# Setup the development database for Django - you only need to do this once.
sudo docker-compose run web ./manage.py migrate

# Bring up development container - will show Django dev server logs
sudo make web

# In another console window/tab, run this to build the JavaScript / CSS,
# and see the webpack build output
sudo make webpack
```

Now you should be able to visit [`http://localhost:8000`](http://localhost:8000) and see the Clerk site.
