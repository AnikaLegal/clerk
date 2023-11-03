## Docker

The environment for this app is built using Docker, and the app runs in production using Docker Swarm. Our The `docker` directory has the following files:

- Dockerfile.base: base Docker image, used to build [anikalaw/clerkbase](https://hub.docker.com/repository/docker/anikalaw/clerkbase)
- Dockerfile: final Docker image, used to build [anikalaw/clerk](https://hub.docker.com/repository/docker/anikalaw/clerk)
- docker.compose.local.yml: Docker Compose config for local development
- docker.compose.staging.yml: Docker Swarm config for test environment
- docker.compose.prod.yml: Docker Swarm config for prod environment

## Deployment

Deployment is done via a GitHub workflow [here](https://github.com/AnikaLegal/clerk/actions?query=workflow%3ADeploy.) A deployment involves SSHing into the target server and updating the Docker Swarm config. Deployment must be manually triggered from GitHub. There are two environments to deploy to, test and prod:

- [test backend](https://test-clerk.anikalegal.com/admin), which is deployed to by `develop`, used by the [test frontend](https://test-repairs.anikalegal.com)
- [prod backend](https://clerk.anikalegal.com/admin), which is deployed to by `master`, used by the [prod frontend](https://repairs.anikalegal.com)

When making a change or bugfix, you should:

- create a feature branch from `develop` called `feature/my-branch-name` and test it locally
- merge the branch into `develop` and trigger a release to the test environment
- check your changes in the test environment
- merge the `develop` into `master` trigger a release of your change to prod

## Infrastructure

![infra](./img/infra.png)

There are two containers that run the application. A Django web server and a [Django Q](https://django-q.readthedocs.io/en/latest/) worker server. Both connect to a common database.

The application runs on Docker Swarm. The test and prod environments both run on a single AWS EC2 instance. That instance also contains the PostgreSQL database and a NGINX server which reverse proxies requests into the Docker containers.

Database backups are taken manually and stored in `s3://anika-database-backups`. Uploaded files are stored in `s3://anika-clerk` and `s3://anika-clerk-test`. Other than uploaded files and the contents of the PostgreSQL database, there is no important state on the EC2 instance or Docker images, which can be blown away and rebuilt at will. The only thing that will change is that EC2 instance IP address, which will need to be updated in CloudFlare.

DNS is handled by [CloudFlare](https://dash.cloudflare.com/7de9e8b83e7f8e80bdb5f40ec9e0ef22/anikalegal.com/dns), which also does SSL termination for us.

Emails are sent using [SendGrid](https://app.sendgrid.com).

Infra config can be found in the [infra](https://github.com/AnikaLegal/infra) repo.

## Logging and Error Reporting

- All application logs are logged to [Sumo Logic](https://service.au.sumologic.com/ui/).
- Errors are reported to [Sentry](https://sentry.io/organizations/anika-legal/projects/).
- Application uptime is tracked by [StatusCake](https://app.statuscake.com/YourStatus.php).
