# Clerk task runner.
#
# Requires just >= 1.46 (uses the [arg(...)] attribute for --long / -short flags).
# All recipes run from the project root. Run `just` (or `just --list`) to see them.

set shell := ["bash", "-c"]
set default-list := true


app_name := "clerk"
compose := "docker compose -p clerk -f docker/docker-compose.local.yml"

# Show usage for a recipe, e.g. `just help build`
[arg("recipe", help="Recipe to show usage for")]
help recipe:
    @{{just_executable()}} --usage {{recipe}}

# Regenerate OpenAPI schema and JavaScript API client
schema:
    cd frontend && npm run schema

# Build images locally (no target: frontend + backend; or any of: backend | frontend | base)
[arg("no_cache", long="no-cache", short="n", value="1", help="Build without the Docker cache")]
[arg("targets", help="backend | frontend | base (default: frontend + backend)")]
build no_cache="" *targets:
    #!/usr/bin/env bash
    set -euo pipefail
    j="{{just_executable()}}"
    nc=""; [ -n "{{no_cache}}" ] && nc="--no-cache"
    targets="{{targets}}"
    [ -z "$targets" ] && targets="frontend backend"
    for t in $targets; do
      case "$t" in
        backend|frontend|base) "$j" build-"$t" $nc ;;
        *)
          echo "Unknown build target: $t (expected backend, frontend, or base)" >&2
          exit 1
          ;;
      esac
    done

# Build the backend (app) image
[private]
[arg("no_cache", long="no-cache", short="n", value="1", help="Build without the Docker cache")]
build-backend no_cache="":
    docker build {{ if no_cache != "" { "--no-cache" } else { "" } }} --file docker/Dockerfile --tag {{app_name}}:local .

# Build the frontend image
[private]
[arg("no_cache", long="no-cache", short="n", value="1", help="Build without the Docker cache")]
build-frontend no_cache="":
    docker build {{ if no_cache != "" { "--no-cache" } else { "" } }} --file docker/Dockerfile.frontend --tag {{app_name}}-frontend:local .

# Build the multi-platform base image
[private]
[arg("no_cache", long="no-cache", short="n", value="1", help="Build without the Docker cache")]
build-base no_cache="":
    docker build --platform=linux/amd64,linux/arm64 {{ if no_cache != "" { "--no-cache" } else { "" } }} --file docker/Dockerfile.base --tag anikalaw/clerkbase:latest .

# Run Django dev server within a Docker container
dev:
    {{compose}} up web

# Stop Docker Compose
down:
    {{compose}} down

# Run Django dev server with debug ports
debug:
    {{compose}} run --rm --service-ports web

# Restart Docker Compose service
[arg("service_name", help="Docker Compose service to restart")]
restart service_name:
    {{compose}} restart {{service_name}}

# View logs for Docker Compose service
[arg("service_name", help="Docker Compose service to tail logs for")]
logs service_name:
    {{compose}} logs --tail 200 -f {{service_name}}

# SSH into a remote server (reads CLERK_HOST from env/<env>.env)
[arg("env", long="env", short="e", help="Environment file to read CLERK_HOST from (env/<env>.env)")]
ssh env="prod":
    #!/usr/bin/env bash
    set -euo pipefail
    file="env/{{env}}.env"
    if [ ! -f "$file" ]; then
      echo "Failed to load $file file"
      exit 1
    fi
    host=$(grep -E '^CLERK_HOST=' "$file" | tail -n1 | cut -d= -f2-)
    host="${host%\"}"
    host="${host#\"}"
    if [ -z "$host" ]; then
      echo "Failed to load $file file"
      exit 1
    fi
    cmd="ssh root@${host}"
    echo "$cmd"
    exec $cmd

# Add ngrok URL to SendGrid to receive emails on dev address
[arg("url", help="Public ngrok URL to register with SendGrid")]
ngrok url:
    {{compose}} run --rm web ./manage.py setup_dev_inbound_emails {{url}}

# Create case documents from templates for local development & testing
[arg("fileref", help="Case fileref to create documents for")]
docs fileref:
    {{compose}} run --rm web ./manage.py set_up_case_docs {{fileref}}

# Assert file ownership of project
[arg("user", long="user", short="u", help="Owner for the files (default: current $USER)")]
own user="":
    #!/usr/bin/env bash
    set -euo pipefail
    user="{{user}}"
    if [ -z "$user" ]; then
      user="$USER"
    fi
    sudo chown -R "$user": .

# Stop all running Docker containers
kill:
    #!/usr/bin/env bash
    set -e
    docker update --restart=no $(docker ps -q)
    docker kill $(docker ps -q)

# Clean Docker environment
[arg("volumes", long="volumes", short="v", value="1", help="Also remove Docker volumes")]
[arg("images", long="images", short="i", value="1", help="Also remove Docker images")]
clean volumes="" images="":
    #!/usr/bin/env bash
    set -euo pipefail
    running=$(docker ps -q | tr '\n' ' ')
    if [ -n "${running// }" ]; then
      docker kill $running
    fi
    all=$(docker ps -a -q | tr '\n' ' ')
    if [ -n "${all// }" ]; then
      docker rm $all
    fi
    if [ -n "{{images}}" ]; then
      imgs=$(docker images -q | tr '\n' ' ')
      if [ -n "${imgs// }" ]; then
        docker rmi $imgs
      fi
    fi
    if [ -n "{{volumes}}" ]; then
      vols=$(docker volume ls -q | tr '\n' ' ')
      if [ -n "${vols// }" ]; then
        docker volume rm $vols
      fi
    fi

# Get a bash shell in a Docker container
[arg("frontend", long="frontend", short="f", value="1", help="Shell into the frontend service instead of web")]
bash frontend="":
    #!/usr/bin/env bash
    set -euo pipefail
    service="web"
    if [ -n "{{frontend}}" ]; then
      service="frontend"
    fi
    {{compose}} run --rm "$service" bash

# Get a Django shell in a Docker container
[arg("print_sql", long="print-sql", short="p", value="1", help="Print SQL for each query (shell_plus --print-sql)")]
[arg("debug", long="debug", short="d", value="1", help="Run under debugpy on port 8123")]
shell print_sql="" debug="":
    #!/usr/bin/env bash
    set -euo pipefail
    cmd="shell_plus"
    if [ -n "{{print_sql}}" ]; then
      cmd="$cmd --print-sql"
    fi
    debug_args=""
    if [ -n "{{debug}}" ]; then
      debug_args="-p 8123:8123 -e DEBUGPY=true"
    fi
    {{compose}} run --rm $debug_args web ./manage.py $cmd

# Get a PostgreSQL shell in a Docker container
psql:
    {{compose}} run --rm web psql

# Run pytest in the test container; extra args pass through (leading app/ stripped, dashed flags after --)
[arg("interactive", long="interactive", short="i", value="1", help="Open a shell in the test container instead of running pytest")]
[arg("debug", long="debug", short="d", value="1", help="Run under debugpy on port 8123")]
[arg("FLAGS", help="Args passed to pytest; put dashed flags after -- (e.g. -- -k EXPR)")]
test interactive="" debug="" *FLAGS:
    #!/usr/bin/env bash
    set -euo pipefail
    export DJANGO_SETTINGS_MODULE={{app_name}}.settings.test
    if [ -n "{{interactive}}" ]; then
      cmd="bash"
    else
      # Strip a host-style "app/" prefix from each arg; pytest runs from /app in the container.
      given="{{FLAGS}}"
      stripped=""
      for a in $given; do stripped="$stripped ${a#app/}"; done
      cmd="python -Xfrozen_modules=off -m pytest$stripped"
    fi
    debug_args=""
    if [ -n "{{debug}}" ]; then
      debug_args="-p 8123:8123 -e DEBUGPY=true"
    fi
    {{compose}} run --rm $debug_args test $cmd

# Obfuscate personally identifiable info
[arg("debug", long="debug", short="d", value="1", help="Run under debugpy on port 8123")]
obfuscate debug="":
    #!/usr/bin/env bash
    set -euo pipefail
    debug_args=""
    if [ -n "{{debug}}" ]; then
      debug_args="-p 8123:8123 -e DEBUGPY=true"
    fi
    {{compose}} run --rm $debug_args web ./manage.py obfuscate_data

# Reset local database
reset:
    {{compose}} run --rm web /app/scripts/tasks/dev-reset.sh

# Restore local database from staging backups
restore:
    {{compose}} run --rm web /app/scripts/tasks/dev-restore.sh

# Create and apply local database migrations
migrate:
    {{compose}} run --rm web bash -c "./manage.py makemigrations && ./manage.py migrate"

# Create superuser for local development & testing
[arg("email", help="Email address (also used as the username)")]
superuser email:
    {{compose}} run --rm web ./manage.py createsuperuser --no-input --username {{email}} --email {{email}}
