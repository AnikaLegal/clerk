#!/bin/bash
docker-compose \
    -f docker/docker-compose.local.yml \
    run --rm web \
    ./manage.py setup_dev_inbound_emails "$1"

