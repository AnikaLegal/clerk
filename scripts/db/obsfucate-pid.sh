#!/bin/bash
# Obsfucate personally identifiable info from prod
docker-compose -f docker/docker-compose.local.yml run --rm web ./manage.py obsfucate_actionstep_data
