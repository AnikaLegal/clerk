#!/usr/bin/env bash
# Saves each Clerk query's result for a month as a test fixture, from the
# local database (just dev). Usage: test/fixtures.sh 2026-02-01
set -euo pipefail
month="$1"
here="$(cd "$(dirname "$0")" && pwd)"
for slide in 4 5 6 7 8 9; do
    query="$(sed -e 's/;[[:space:]]*$//' "$here/../blocks/slide$slide.sql")"
    docker exec -i clerk_db psql -U postgres -At -v month="'$month'" \
        > "$here/fixtures/slide$slide-$month.json" <<SQL
SELECT coalesce(json_agg(t), '[]') FROM ($query) t;
SQL
done
