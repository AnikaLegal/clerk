## Docker

The environment for this app is built using Docker, and the app runs in production using Docker Swarm. Our The `docker` directory has the following files:

- Dockerfile.base: base Docker image, used to build [anikalaw/clerkbase](https://hub.docker.com/repository/docker/anikalaw/clerkbase)
- Dockerfile: final Docker image, used to build [anikalaw/clerk](https://hub.docker.com/repository/docker/anikalaw/clerk)
- docker.compose.local.yml: Docker Compose config for local development
- docker.compose.staging.yml: Docker Swarm config for staging environment
- docker.compose.prod.yml: Docker Swarm config for production environment

## Deployment

Deployment is done via a GitHub workflow [here](https://github.com/AnikaLegal/clerk/actions?query=workflow%3ADeploy). A deployment involves SSHing into the target server and updating the Docker Swarm config. Deployment must be manually triggered from GitHub. There are two environments to deploy to, staging and production:

- [staging backend](https://test-clerk.anikalegal.com/admin), which is deployed to by `develop` branch, used by the [staging frontend](https://test-intake.anikalegal.com)

- [production backend](https://clerk.anikalegal.com/admin), which is deployed to by `master` branch, used by the [production frontend](https://intake.anikalegal.com)

When making a change or bugfix, you should:

- create a branch from `develop` called e.g. `feature/my-branch-name` and test it locally
- merge the branch into `develop` and trigger a release to the staging environment
- check your changes in the staging environment
- merge the `develop` branch into `master` and trigger a release to the production environment

## Infrastructure

![infra](./img/infra.png)

There are two containers that run the application. A Django web server and a [Django Q](https://django-q2.readthedocs.io/en/master/) worker server. Both connect to a common database.

The application runs on Docker Swarm. The test and prod environments both run on a single AWS EC2 instance. That instance also contains the PostgreSQL database and a NGINX server which reverse proxies requests into the Docker containers.

Production database backups are automated via GitHub Actions and stored in `s3://anika-database-backups`. Uploaded files are stored in `s3://anika-clerk` and `s3://anika-clerk-test`. Other than uploaded files and the contents of the PostgreSQL database, there is no important state on the EC2 instance or Docker images, which can be blown away and rebuilt at will. The only thing that will change is that EC2 instance IP address, which will need to be updated in CloudFlare.

DNS is handled by [CloudFlare](https://dash.cloudflare.com/7de9e8b83e7f8e80bdb5f40ec9e0ef22/anikalegal.com/dns), which also does SSL termination for us.

Emails are sent using [SendGrid](https://app.sendgrid.com).

Infrastructure configuration and scripts can be found under the `infra` directory.

## Logging and Error Reporting

- All application logs are logged to [Sumo Logic](https://service.au.sumologic.com/ui/).
- Errors are reported to [Sentry](https://sentry.io/organizations/anika-legal/projects/).
- Application uptime is tracked by [StatusCake](https://app.statuscake.com/YourStatus.php).
