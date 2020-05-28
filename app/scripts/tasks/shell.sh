#!/bin/bash
set -e
watchmedo \
    auto-restart \
    --directory /app/ \
    --recursive \
    --pattern '*.py' \
    -- \
    ./manage.py shell_plus
