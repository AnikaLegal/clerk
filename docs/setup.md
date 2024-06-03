## Prerequisites for Local Development

This repository should work on Linux and Mac.

You will need:

- `docker` ([install](https://docs.docker.com/install/#supported-platforms))
- `docker-compose` ([install](https://docs.docker.com/compose/install/))
- `transcrypt` ([install](https://github.com/elasticdog/transcrypt#usage))
- `inv` ([install](https://www.pyinvoke.org/installing.html))

## Optional for Local Development

- `ngrok` ([install](https://docs.docker.com/install/#supported-platforms))

  For testing inbound emails.

## Getting Started

If you are using Windows ensure that git is setup to use LF not CLRF

```
git config core.autocrlf false
git rm --cached -r .
git reset --hard
```

Environment variables are stored in .env files and encrypted using transcrypt.
You can list all encrypted files with `transcrypt --list`.

To intialise the repository on cloning, run:

```bash
transcrypt -c aes-256-cbc -p $TRANSCRYPT_PASSWORD
```

The transcrypt password is available in the Tech team Bitwarden account.

Next, build the Docker environment that we'll be using:

```bash
# Build Webpack container
inv build -w
# Build Django container
inv build
```

You can set up your database with the `reset` command:

```bash
inv reset
```

Create a user for local development and testing using your Anika email address:

```bash
inv superuser your.name@anikalegal.com
```

Finally you can bring up the web server:

```bash
inv dev
```

You should now be able to access:

- The Anika website at [`http://localhost:8000`](http://localhost:8000).
- The Clerk CMS at [`http://localhost:8000/clerk`](http://localhost:8000/clerk).
- The Django Admin Interface at
  [`http://localhost:8000/admin`](http://localhost:8000/admin).

You can list other available commands using the `--list` argument of the
`invoke` command:

```bash
inv -l
```
