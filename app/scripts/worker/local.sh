#!/bin/bash
set -e
watchmedo \
    auto-restart \
    --directory /app/ \
    --recursive \
    --pattern '*.py' \
    -- \
    python -Xfrozen_modules=off manage.py qcluster
