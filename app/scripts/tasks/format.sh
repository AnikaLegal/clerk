#!/bin/bash
black \
    --line-length 90 \
    --exclude "frontend/|migrations/" \
    --skip-string-normalization \
    .
isort \
    -l 90 \
    --skip migrations --skip /app/frontend \
    --apply