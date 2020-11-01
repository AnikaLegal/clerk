#!/bin/bash
set -e
cd /app/
watchmedo \
    auto-restart \
    --directory /app/ \
    --recursive \
    --pattern '*.py' \
    -- \
    streamlit run dash.py