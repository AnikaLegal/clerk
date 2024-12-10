from invoke import task

APP_NAME = "clerk"
HOST = "13.55.250.149"
COMPOSE = "docker compose -p clerk -f docker/docker-compose.local.yml"


@task
def schema(c):
    """Regenerate OpenAPI schema and JavaScript API client"""
    c.run("cd frontend && npm run schema")


@task
def build(c, base=False, webpack=False, no_cache=False):
    """Build Docker environment locally"""

    file = "Dockerfile"
    tag = f"{APP_NAME}:local"
    if base:
        file = "Dockerfile.base"
        tag = "anikalaw/clerkbase:latest"
    elif webpack:
        file = "Dockerfile.webpack"
        tag = f"{APP_NAME}-webpack:local"

    args = ""
    if no_cache:
        args += "--no-cache"

    c.run(f"docker build {args} --file docker/{file} --tag {tag} .")


@task
def dev(c):
    """Run Django dev server within a Docker container"""
    c.run(f"{COMPOSE} up web", pty=True)


@task
def down(c):
    """Stop Docker Compose"""
    c.run(f"{COMPOSE} down", pty=True)


@task
def debug(c):
    """Run Django dev server with debug ports"""
    c.run(f"{COMPOSE} run --rm --service-ports web", pty=True)


@task
def restart(c, service_name):
    """Restart Docker Compose service"""
    c.run(f"{COMPOSE} restart {service_name}", pty=True)


@task
def logs(c, service_name):
    """View logs for Docker Compose service"""
    c.run(f"{COMPOSE} logs --tail 200 -f {service_name}", pty=True)


@task
def ssh(c):
    """SSH into prod"""
    cmd = f"ssh root@{HOST}"
    print(cmd)
    c.run(cmd, pty=True)


@task
def ngrok(c, url):
    """Add ngrok URL to SendGrid to receive emails on dev address"""
    run(c, f"./manage.py setup_dev_inbound_emails {url}")


@task
def own(c, user=None):
    """Assert file ownership of project"""
    if not user:
        import os

        user = os.getenv("USER")
    c.run(f"sudo chown -R {user}: .", pty=True)


@task
def kill(c):
    """Stop all running Docker containers"""
    c.run("docker update --restart=no `docker ps -q`")
    c.run("docker kill $(docker ps -q)")


@task
def clean(c, volumes=False, images=False):
    """Clean Docker environment"""

    result = c.run("docker ps -q").stdout.strip().replace("\n", " ")
    if result:
        c.run(f"docker kill {result}")
    result = c.run("docker ps -a -q").stdout.strip().replace("\n", " ")
    if result:
        c.run(f"docker rm {result}")

    if images:
        result = c.run("docker images -q").stdout.strip().replace("\n", " ")
        if result:
            c.run(f"docker rmi {result}")

    if volumes:
        result = c.run("docker volume ls -q").stdout.strip().replace("\n", " ")
        if result:
            c.run(f"docker volume rm {result}")


@task
def bash(c, webpack=False):
    """Get a bash shell in a Docker container"""
    s = "webpack" if webpack else "web"
    run(c, "bash", service=s)


@task
def shell(c, print_sql=False):
    """Get a Django shell in a Docker container"""
    cmd = "shell_plus"
    if print_sql:
        cmd += " --print-sql"
    run(c, f"./manage.py {cmd}")


@task
def psql(c):
    """Get a PostgreSQL shell in a Docker container"""
    run(c, "psql")


@task(incrementable=["verbose"])
def test(
    c,
    recreate=False,
    interactive=False,
    quiet=False,
    verbose=0,
    debug=False,
):
    """Run pytest"""
    if interactive:
        cmd = "bash"
    else:
        cmd = "pytest"
        if recreate:
            cmd += " --create-db"
        else:
            cmd += " --reuse-db"

        if quiet:
            cmd += " --quiet --no-summary --exitfirst"
        elif verbose:
            cmd += " -" + ("v" * verbose)

    debug_args = ""
    if debug:
        debug_args = "-p 8123:8123 -e DEBUG_PYTEST=true"

    c.run(
        f"{COMPOSE} run --rm {debug_args} test {cmd}",
        pty=True,
        env={
            "DJANGO_SETTINGS_MODULE": f"{APP_NAME}.settings.test",
        },
    )


@task
def obfuscate(c):
    """Obfuscate personally identifiable info"""
    run(c, "./manage.py obfuscate_data")


@task
def reset(c):
    """Reset local database"""
    run(c, "/app/scripts/tasks/dev-reset.sh")


@task()
def restore(c):
    """Restore local database from staging backups"""
    run(c, "/app/scripts/tasks/dev-restore.sh")


@task
def migrate(c):
    """Create and apply local database migrations"""
    run(c, 'bash -c "./manage.py makemigrations && ./manage.py migrate"')


@task
def superuser(c, email):
    """Create superuser for local development & testing"""
    run(c, f"./manage.py createsuperuser --no-input --username {email} --email {email}")


def run(c, cmd: str, service="web"):
    c.run(f"{COMPOSE} run --rm {service} {cmd}", pty=True)
