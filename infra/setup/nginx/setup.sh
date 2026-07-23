#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

echo -e "\n>>> Installing NGINX"
export LC_ALL=C.UTF-8
export DEBIAN_FRONTEND=noninteractive
# Restart services automatically instead of prompting (needrestart)
export NEEDRESTART_MODE=a
apt-get install --yes nginx

echo -e "\n>>> Copying NGINX config"
cp /srv/infra/nginx/nginx.conf /etc/nginx/nginx.conf
rm -f /etc/nginx/sites-enabled/default
cp /srv/infra/nginx/website.conf /etc/nginx/sites-enabled/

echo -e "\n>>> Testing NGINX config"
nginx -t

echo -e "\n>>> Reloading NGINX config"
# reload-or-restart also covers the case where nginx is installed but not
# running, which plain "nginx -s reload" does not.
systemctl enable nginx
systemctl reload-or-restart nginx

echo -e "\n>>> Finished installing NGINX"
