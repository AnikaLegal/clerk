from invoke import task

APP_NAME = "clerk"
HOST = "13.55.250.149"
COMPOSE = "docker compose -p clerk -f docker/docker-compose.local.yml"


@task
def schema(c):
    """Regenerate OpenAPI schema and JavaScript API client"""
    c.run("cd frontend && npm run schema")


@task
def build(c, base=False, frontend=False, no_cache=False):
    """Build Docker environment locally"""

    file = "Dockerfile"
    tag = f"{APP_NAME}:local"
    args = ""

    if base:
        file = "Dockerfile.base"
        tag = "anikalaw/clerkbase:latest"
        args += " --platform=linux/amd64,linux/arm64"
    elif frontend:
        file = "Dockerfile.frontend"
        tag = f"{APP_NAME}-frontend:local"

    if no_cache:
        args += " --no-cache"

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
def docs(c, fileref):
    """Create case documents from templates for local development & testing"""
    run(c, f"./manage.py set_up_case_docs {fileref}")


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
def bash(c, frontend=False):
    """Get a bash shell in a Docker container"""
    s = "frontend" if frontend else "web"
    run(c, "bash", service=s)


@task
def shell(c, print_sql=False, debug=False):
    """Get a Django shell in a Docker container"""
    cmd = "shell_plus"
    if print_sql:
        cmd += " --print-sql"
    run(c, f"./manage.py {cmd}", debug=debug)


@task
def psql(c):
    """Get a PostgreSQL shell in a Docker container"""
    run(c, "psql")


@task(incrementable=["verbose"])
def test(
    c,
    path=None,
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
        cmd = "python -Xfrozen_modules=off -m pytest"
        if recreate:
            cmd += " --create-db"
        else:
            cmd += " --reuse-db"

        if quiet:
            cmd += " --quiet --no-summary --exitfirst"
        elif verbose:
            cmd += " -" + ("v" * verbose)

        if path:
            cmd += f" {path}"

    env = {
        "DJANGO_SETTINGS_MODULE": f"{APP_NAME}.settings.test",
    }
    run(c, cmd, service="test", env=env, debug=debug)


@task
def obfuscate(c, debug=False):
    """Obfuscate personally identifiable info"""
    run(c, "./manage.py obfuscate_data", debug=debug)


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


def run(c, cmd: str, service="web", env: dict = {}, debug=False):
    debug_args = ""
    if debug:
        debug_args = "-p 8123:8123 -e DEBUGPY=true"
    c.run(f"{COMPOSE} run --rm {debug_args} {service} {cmd}", pty=True, env=env)
