#!/bin/bash
# Lint Python code
set -e
flake8 \
    --max-line-length=90 \
    --exclude='*migrations*,/app/frontend' \
    .
isort \
    -l 90 \
    --diff \
    --check-only \
    --skip migrations --skip /app/frontend