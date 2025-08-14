#!/usr/bin/env bash

set -o errexit
export DEBUGPY=true

watchmedo \
    auto-restart \
    --directory /app/ \
    --recursive \
    --pattern '*.py;*.html;*.css' \
    --signal SIGHUP \
    -- \
    python -Xfrozen_modules=off manage.py runserver --noreload 0.0.0.0:8000