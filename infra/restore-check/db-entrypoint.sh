#!/usr/bin/env bash

# Entrypoint for the restore check container (run under the timeout
# failsafe, see Dockerfile.database): bring up a throwaway Postgres using the
# image's own entrypoint, wait until it accepts TCP connections, then hand
# over to the check so its exit status becomes the container's. Trust auth
# is deliberate: the task accepts no ingress, holds nothing but scratch
# data, and dies with the run.

set -o errexit
set -o nounset
set -o pipefail

export POSTGRES_HOST_AUTH_METHOD=trust
docker-entrypoint.sh postgres &

# PGHOST=localhost checks TCP, so the init-time server (unix socket only)
# cannot satisfy the wait.
export PGHOST=localhost PGPORT=5432 PGUSER=postgres
echo ">>> Waiting for Postgres to accept connections"
for _ in $(seq 1 60); do
    if pg_isready --quiet; then
        break
    fi
    sleep 1
done
pg_isready --quiet # fail the task loudly if Postgres never came up

exec python3 /db-check.py
