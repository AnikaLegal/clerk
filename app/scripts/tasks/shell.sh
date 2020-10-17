#!/bin/bash
set -e
watchmedo \
    auto-restart \
    --directory /app/ \
    --recursive \
    --pattern '*.py' \
    -- \
    python3.8 ./manage.py shell_plus
