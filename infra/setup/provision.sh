#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

prog=$(basename "$0")
base_dir="$(dirname -- $(dirname -- $(cd -- "$(dirname -- $0)" &> /dev/null && pwd)))"

usage() {
    echo "Usage: $prog <HOST> [--force]"
    echo ""
    echo "Provision HOST as a Clerk server (NGINX, Postgres, Docker Swarm,"
    echo "AWS CLI, hardening). Aborts if HOST looks like it is already set"
    echo "up; pass --force to re-run the setup scripts anyway."
}

HOST=""
FORCE=false
while [ $# -gt 0 ]; do
    case "$1" in
        -f|--force)
            FORCE=true
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            if [ -n "$HOST" ]; then
                usage
                exit 1
            fi
            HOST=$1
            ;;
    esac
    shift
done
if [ -z "$HOST" ]; then
    usage
    exit 1
fi

# Automatically accept the host key of a newly provisioned server, but still
# fail on a changed host key. This lets the script run unattended without
# relying on the operator's ssh config.
SSH_OPTS="-o StrictHostKeyChecking=accept-new"

echo -e "\n>>> Setting up $HOST"
cd $base_dir

if ssh $SSH_OPTS root@$HOST '[ -d /srv/infra/ ]'; then
    if [ "$FORCE" != "true" ]; then
        echo -e "\nError: host $HOST is already set up. Pass --force to re-run setup." >&2
        exit 1
    fi
    echo -e "\n>>> Host $HOST is already set up, continuing (--force)"
fi

echo -e "\n>>> Copying infra files to $HOST"
# NOTE: don't copy top-level scripts as they are intended to be run from the
# local machine only.
rsync -av --delete --delete-before --filter='- /*.sh' -e "ssh $SSH_OPTS" infra/setup/ root@$HOST:/srv/infra

ssh $SSH_OPTS root@$HOST localectl set-locale LANG=en_US.UTF-8
unset LC_ALL
unset LC_CTYPE

echo -e "\n>>> Updating apt sources on $HOST"
ssh $SSH_OPTS root@$HOST apt-get update -qq --yes

echo -e "\n>>> Setting up NGINX on $HOST"
ssh $SSH_OPTS root@$HOST /srv/infra/nginx/setup.sh

echo -e "\n>>> Setting up Postgres on $HOST"
ssh $SSH_OPTS root@$HOST /srv/infra/postgres/setup.sh

echo -e "\n>>> Setting up Docker on $HOST"
ssh $SSH_OPTS root@$HOST /srv/infra/docker/setup.sh

echo -e "\n>>> Setting up AWS CLI on $HOST"
ssh $SSH_OPTS root@$HOST /srv/infra/aws/setup.sh

echo -e "\n>>> Hardening server on $HOST"
ssh $SSH_OPTS root@$HOST /srv/infra/security/setup.sh

echo -e "\n>>> Finished setting up $HOST"
exit 0
