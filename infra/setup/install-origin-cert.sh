#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

prog=$(basename "$0")

usage() {
    echo "Usage: $prog <HOST> <CERT_FILE> <KEY_FILE>"
    echo ""
    echo "Install the Cloudflare origin certificate and private key on HOST"
    echo "and reload NGINX if it is running. Run before provision.sh on a new"
    echo "server. The key is kept only on HOST: delete KEY_FILE afterwards."
}

if [ -z "${1:-}" ] || [ -z "${2:-}" ] || [ -z "${3:-}" ]; then
    usage
    exit 1
fi
HOST=$1
CERT_FILE=$2
KEY_FILE=$3

SSH_OPTS="-o StrictHostKeyChecking=accept-new"
CERT_DIR="/etc/ssl/cloudflare"

echo -e "\n>>> Installing the origin certificate on $HOST"
ssh $SSH_OPTS "root@$HOST" "install -d -m 755 $CERT_DIR"
ssh $SSH_OPTS "root@$HOST" "umask 022 && cat > $CERT_DIR/origin.pem" < "$CERT_FILE"
ssh $SSH_OPTS "root@$HOST" "umask 077 && cat > $CERT_DIR/origin.key" < "$KEY_FILE"

echo -e "\n>>> Checking the key matches the certificate"
ssh $SSH_OPTS "root@$HOST" "cmp \
    <(openssl x509 -noout -pubkey -in $CERT_DIR/origin.pem) \
    <(openssl pkey -pubout -in $CERT_DIR/origin.key)"
ssh $SSH_OPTS "root@$HOST" "openssl x509 -noout -subject -ext subjectAltName -enddate -in $CERT_DIR/origin.pem"

if ssh $SSH_OPTS "root@$HOST" "systemctl is-active --quiet nginx"; then
    echo -e "\n>>> Reloading NGINX"
    ssh $SSH_OPTS "root@$HOST" "nginx -t && systemctl reload nginx"
fi

echo -e "\n>>> Finished installing the origin certificate on $HOST"
