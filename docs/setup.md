## Prerequisites for Local Development

You will need:

- `docker` ([install](https://docs.docker.com/install/#supported-platforms))
- `docker-compose` ([install](https://docs.docker.com/compose/install/))

## Getting Started

First, add a file called `.env` to the repository root with the following contents:

```text
AZURE_AD_CLIENT_ID=
AZURE_AD_CLIENT_SECRET=
SENDGRID_API_KEY=
MAILCHIMP_API_KEY=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
ACTIONSTEP_CLIENT_ID=
ACTIONSTEP_CLIENT_SECRET=
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
GOOGLE_OAUTH2_KEY=
GOOGLE_OAUTH2_SECRET=
```

The values of these secrets will be provided to you if you need them. They should be available in the Tech team Bitwarden account.

Next, you want to build the Docker environment that we'll be using:

```bash
make build
```

Now you can set up your database with this reset script:

```bash
./scripts/db/reset.sh
```

To do this manually, you can to get a bash shell into the web container and run a Django database migration:

```bash
# Get a bash shell in the container
make bash

# Setup the development database for Django - you only need to do this once.
./manage.py migrate

# Create a local admin user
./manage.py createsuperuser
```

Finallly you can exit the container shell and bring up the webserver:

```bash
make web
```

Now you should be able to visit [`http://localhost:8000/admin`](http://localhost:8000/admin) and see the Clerk site.

You can also get a Django shell running using:

```bash
make shell
```
