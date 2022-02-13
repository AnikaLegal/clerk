from invoke import task

APP_NAME = "clerk"
HOST = "3.106.55.74"
COMPOSE = "docker-compose -p clerk -f docker/docker-compose.local.yml"
BACKUP_BUCKET_NAME = "anika-database-backups"


@task
def build(c):
    """Build Docker environment locally"""
    c.run(f"docker build -f docker/Dockerfile -t {APP_NAME}:local .")


@task
def dev(c):
    """Run Django dev server within a Docker container"""
    c.run(f"{COMPOSE} run --rm --service-ports web", pty=True)


@task
def worker(c):
    """View worker logs"""
    c.run(f"{COMPOSE} logs --tail 100 -f worker ", pty=True)


@task
def ssh(c):
    """SSH into prod"""
    print(f"ssh root@{HOST}")


@task
def ngrok(c, url):
    """Add ngrok URL to sendgrid to receive emails on dev address"""
    run_web(c, f"./manage.py setup_dev_inbound_emails {url}")


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
def bash(c):
    """Get a bash shell in a Docker container)"""
    run_web(c, "bash")


@task
def shell(c):
    """Get a Django shell in a Docker container"""
    run_web(c, "./manage.py shell_plus")


@task
def psql(c):
    """Get a Django shell in a Docker container"""
    run_web(c, "psql")


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
    print("\nResetting database")
    run_web(c, "./manage.py reset_db --close-sessions --noinput")
    _post_reset(c)
    print("\nDatabase reset finished.")


@task
def restore(c):
    """Reset local database"""
    print("\nResetting database")
    run_web(c, "./manage.py reset_db --close-sessions --noinput")

    s3_bucket = f"s3://{BACKUP_BUCKET_NAME}"
    print(f"\nRestoring database from S3 backups at {s3_bucket}")
    result = c.run(
        (
            f"aws --profile anika s3 ls {s3_bucket} | "
            "sort | grep postgres_clerk | "
            "tail -n 1 | "
            "awk '{{print $4}}'"
        ),
        pty=True,
    )
    dump_name = result.stdout.strip()
    c.run(
        (
            f"aws --profile anika s3 cp {s3_bucket}/{dump_name} - | gunzip | "
            "pg_restore "
            "--clean "
            "--dbname postgres "
            "--host localhost "
            "--port 25432 "
            "--username postgres "
            "--no-owner"
        ),
        warn=True,
        pty=True,
    )
    _post_reset(c)

    print("\nSetting all Slack messages to send to test alerts channel.")
    shell_cmd = (
        "space=chr(32);"
        "c=SlackChannel.objects.get(name=f'Test{space}Alerts');"
        "SlackMessage.objects.all().update(channel=c);"
        "SlackUser.objects.all().delete()"
    )
    run_web(c, f'./manage.py shell_plus -c "{shell_cmd}"')

    print("\nDeleting all Scheduled tasks and Actionstep access tokens.")
    shell_cmd = (
        "Success.objects.all().delete();"
        "Failure.objects.all().delete();"
        "Schedule.objects.all().delete();"
        "OrmQ.objects.all().delete();"
        "AccessToken.objects.all().delete()"
    )
    run_web(c, f'./manage.py shell_plus -c "{shell_cmd}"')

    print("\nDatabase restore finished.")


def _post_reset(c):
    print("\nRunning migrations")
    run_web(c, "./manage.py migrate")

    print("\nCreating new superuser 'admin'")
    run_web(
        c,
        "./manage.py createsuperuser "
        "--username admin "
        "--email admin@example.com "
        "--noinput",
    )
    print("\nSetting superuser 'admin' password to 12345")
    shell_cmd = "u=User.objects.get(username='admin');u.set_password('12345');u.save();"
    run_web(c, f'./manage.py shell_plus -c "{shell_cmd}"')


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
    run_web(c, "./manage.py migrate_actionstep_paralegals")
    run_web(c, "./manage.py migrate_actionstep_filenotes")
    run_web(c, "./manage.py migrate_actionstep_emails")


@task
def obsfucate(c):
    """Obsfucate personally identifiable info from prod"""
    run_web(c, "./manage.py obsfucate_actionstep_data")


def run_web(c, cmd: str):
    c.run(f"{COMPOSE} run --rm web {cmd}", pty=True)
