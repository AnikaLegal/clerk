#!/bin/bash
set -e
HOST='3.106.55.74'
echo -e "\n>>> SSHing into clerk at $HOST."
ssh -t -o StrictHostKeyChecking=no root@$HOST \
    docker-compose \
        -p task \
        -f /srv/clerk_test/docker-compose.staging.yml \
        run --rm web \
        ./manage.py shell_plus
