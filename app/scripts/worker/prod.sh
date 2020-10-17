#!/bin/bash
set -e
echo "Starting clerk worker as `whoami`"

echo "Setting up logging"
# Set up django logging
touch /var/log/django.log


echo "Starting qcluster"
python3.8 ./manage.py qcluster
