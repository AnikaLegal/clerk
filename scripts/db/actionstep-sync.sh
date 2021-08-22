#!/bin/bash
# Obsfucate pull data from Actionstep prod
docker-compose -f docker/docker-compose.local.yml run --rm web ./manage.py migrate_actionstep_paralegals
docker-compose -f docker/docker-compose.local.yml run --rm web ./manage.py migrate_actionstep_filenotes
