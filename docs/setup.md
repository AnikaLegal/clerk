## Prerequisites for Local Development

This repository should work on Linux and Mac.

You will need:

- `docker` ([install](https://docs.docker.com/install/#supported-platforms))
- `docker-compose` ([install](https://docs.docker.com/compose/install/))
- `transcrypt` ([install](https://github.com/elasticdog/transcrypt#usage))
- `inv` ([install](https://www.pyinvoke.org/installing.html))

## Getting Started

If you are using Windows ensure that git is setup to use LF not CLRF

```
git config core.autocrlf false
git rm --cached -r .
git reset --hard
```

Envars are stored in .env and encrypted using transcrypt. You can see encryoted files with `transcrypt --list`.

To intialise the repository on cloning run

```bash
transcrypt -c aes-256-cbc -p $TRANSCRYPT_PASSWORD
```

The values of these secrets will be provided to you if you need them. They should be available in the Tech team Bitwarden account.

Next, you want to build the Docker environment that we'll be using:

```bash
# Build Webpack container
inv build -w
# Build Django container
inv build
```

Now you can set up your database with this reset command:

```bash
inv reset
```

Finallly you can exit the container shell and bring up the webserver:

```bash
inv dev
```

Now you should be able to visit [`http://localhost:8000/admin`](http://localhost:8000/admin) and see the Clerk site.

You can view other commands with

```bash
inv -l
```
