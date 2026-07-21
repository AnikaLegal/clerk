## Prerequisites for Local Development

This repository should work on Linux and Mac.

You will need:

- `docker` ([install](https://docs.docker.com/install/#supported-platforms))
  You can use [Docker Engine](https://docs.docker.com/engine/install/) on Linux.
- `docker compose (V2)` ([install](https://docs.docker.com/compose/install/))
- `transcrypt` ([install](https://github.com/elasticdog/transcrypt#usage))
- `uv` ([install](https://docs.astral.sh/uv/getting-started/installation/))

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

We use [`just`](https://just.systems) as our task runner. It is installed as a dev
dependency in the app virtualenv, so sync the environment and activate it:

```bash
uv --directory app sync
source app/.venv/bin/activate
```

Activate the virtualenv in each new shell (or add the `source` line to your shell
profile), and run all `just` commands from the project root. Run `just` on its own
to list every recipe, or `just help <recipe>` to see a recipe's usage.

Next, build the Docker containers we'll be using (`just build` builds the
frontend, intake and backend images):

```bash
just build
```

You can set up your database with the `reset` command:

```bash
just reset
```

Create a user for local development and testing using your Anika email address:

```bash
just superuser your.name@anikalegal.com
```

Finally you can bring up the web server:

```bash
just dev
```

You should now be able to access:

- The Anika website at [`http://localhost:8000`](http://localhost:8000).
- The Clerk CMS at [`http://localhost:8000/clerk`](http://localhost:8000/clerk).
- The Django Admin Interface at
  [`http://localhost:8000/admin`](http://localhost:8000/admin).

You can list all available recipes by running `just` with no arguments (or
`just --list`):

```bash
just
```
