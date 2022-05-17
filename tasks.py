from invoke import task

APP_NAME = "clerk"
HOST = "3.106.55.74"
COMPOSE = "docker-compose -p clerk -f docker/docker-compose.local.yml"


@task
def build(c, webpack=False):
    """Build Docker environment locally"""
    if webpack:
        c.run(
            f"docker build -f docker/Dockerfile.webpack -t {APP_NAME}-webpack:local ."
        )
    else:
        c.run(f"docker build -f docker/Dockerfile -t {APP_NAME}:local .")


@task
def dev(c):
    """Run Django dev server within a Docker container"""
    c.run(f"{COMPOSE} up web", pty=True)


@task
def down(c):
    """Stop docker-compose"""
    c.run(f"{COMPOSE} down", pty=True)


@task
def debug(c):
    """Run Django dev server with debug ports"""
    c.run(f"{COMPOSE} run --rm --service-ports web", pty=True)


@task
def restart(c, service_name):
    """Restart Docker-Compose service"""
    c.run(f"{COMPOSE} restart {service_name}", pty=True)


@task
def logs(c, service_name):
    """View logs for Docker-Compose service"""
    c.run(f"{COMPOSE} logs --tail 200 -f {service_name}", pty=True)


@task
def ssh(c):
    """SSH into prod"""
    print(f"ssh root@{HOST}")


@task
def ngrok(c, url):
    """Add ngrok URL to sendgrid to receive emails on dev address"""
    run(c, f"./manage.py setup_dev_inbound_emails {url}")


@task
def own(c, username):
    """Assert file ownership of project"""
    c.run(f"sudo chown -R {username}:{username} .", pty=True)


@task
def kill(c):
    """Stop all running Docker containers"""
    c.run("docker update --restart=no `docker ps -q`")
    c.run("docker kill $(docker ps -q)")


@task
def clean(c):
    """Clean Docker environment"""

    result = c.run("docker ps -q").stdout.strip().replace("\n", " ")
    if result:
        c.run(f"docker kill {result}")
    result = c.run("docker ps -a -q").stdout.strip().replace("\n", " ")
    if result:
        c.run(f"docker rm {result}")
    result = c.run("docker images -q").stdout.strip().replace("\n", " ")
    if result:
        c.run(f"docker rmi {result}")
    result = c.run("docker volume ls -q").stdout.strip().replace("\n", " ")
    if result:
        c.run(f"docker volume rm {result}")


@task
def bash(c, webpack=False):
    """Get a bash shell in a Docker container"""
    s = "webpack" if webpack else "web"
    run(c, "bash", service=s)


@task
def shell(c):
    """Get a Django shell in a Docker container"""
    run(c, "./manage.py shell_plus")


@task
def psql(c):
    """Get a Django shell in a Docker container"""
    run(c, "psql")


@task
def test(c, recreate=False, interactive=False):
    """Run pytest"""
    if interactive:
        c.run(
            f"{COMPOSE} run --rm test bash",
            pty=True,
            env={
                "DJANGO_SETTINGS_MODULE": f"{APP_NAME}.settings.test",
            },
        )

    if recreate:
        cmd = "pytest -vv"
    else:
        cmd = "pytest -vv --reuse-db"
    c.run(
        f"{COMPOSE} run --rm test {cmd}",
        pty=True,
        env={
            "DJANGO_SETTINGS_MODULE": f"{APP_NAME}.settings.test",
        },
    )


@task
def reset(c):
    """Reset local database"""
    run(c, "/app/scripts/tasks/dev-reset.sh")


@task
def restore(c):
    """Reset local database"""
    run(c, "/app/scripts/tasks/dev-restore.sh")


S3_PROD = "anika-clerk"
S3_TEST = "anika-clerk-test"
SYNC_DIRS = [
    "images",
    "original_images",
    "file-uploads",
    "action-documents",
    "email-attachments",
]


@task
def sync_s3(c):
    """
    Sync S3 assets from prod to test
    FIXME: Improve upon public read status.
    """
    for sync_dir in SYNC_DIRS:
        cmd = f"aws --profile anika s3 sync --acl public-read s3://{S3_PROD}/{sync_dir} s3://{S3_TEST}/{sync_dir}"
        c.run(cmd, pty=True)


@task
def sync_actionstep(c):
    """Pull data from Actionstep prod"""
    run(c, "./manage.py migrate_actionstep_paralegals")
    run(c, "./manage.py migrate_actionstep_filenotes")
    run(c, "./manage.py migrate_actionstep_emails")


@task
def obsfucate(c):
    """Obsfucate personally identifiable info from prod"""
    run(c, "./manage.py obsfucate_actionstep_data")


def run(c, cmd: str, service="web"):
    c.run(f"{COMPOSE} run --rm {service} {cmd}", pty=True)
