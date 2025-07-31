#!/bin/bash
set -e
watchmedo \
    auto-restart \
    --directory /app/ \
    --recursive \
    --pattern '*.py;*.html' \
    --signal SIGHUP \
    -- \
    python -Xfrozen_modules=off manage.py runserver --noreload 0.0.0.0:8000