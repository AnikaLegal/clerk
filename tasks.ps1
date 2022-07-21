# Initialise this script by dot sourcing it
#
#    . tasks.ps1
#
# See tasks.py for notes on each task.

$APP_NAME = "clerk"
$COMPOSE = "docker-compose -p clerk -f docker/docker-compose.local.yml"
$BACKUP_BUCKET_NAME = "anika-database-backups"

function build {
    Param(
        [switch]$webpack = $false
    )
    if ($webpack) {
        docker build -f docker/Dockerfile.webpack -t "${APP_NAME}-webpack:local" .
    } else {
        docker build -f docker/Dockerfile -t "${APP_NAME}:local" .
    }
}

function dev {
    Invoke-Expression "$COMPOSE up web"
}

function down {
    Invoke-Expression "$COMPOSE down"
}

function debug {
    Invoke-Expression "$COMPOSE run --rm --service-ports web"
}

function restart {
    Param(
        [string]$service
    )
    Invoke-Expression "$COMPOSE restart $service"
}

function kill {
    docker update --restart=no `docker ps -q
    docker kill $(docker ps -q)
}

function logs {
    Param(
        [string]$service
    )
    Invoke-Expression "$COMPOSE logs -f --tail 200 $service"
}

function reset {
    run -cmd "/app/scripts/tasks/dev-reset.sh"
}


function restore {
    run -cmd "/app/scripts/tasks/dev-restore.sh"
}

function setup-ngrok {
    Param(
        [string]$url
    )
    run -cmd "./manage.py setup_dev_inbound_emails $url"
}

function bash {
    Param(
        [switch]$webpack = $false
    )
    if ($webpack) {
        run -cmd "bash" -service "webpack"
    } else {
        run -cmd "bash" -service "web"
    }
}

function shell {
    run -cmd "./manage.py shell_plus"
}

function psql {
    run -cmd "psql"
}

function run {
    Param(
        [string]$cmd,
        [string]$service="web"
    )
    Invoke-Expression "$COMPOSE run --rm $service $cmd"
}