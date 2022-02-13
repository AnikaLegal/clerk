#!/bin/bash
set -e
echo -e "\n>>> Installing NGINX"
apt-get install --yes nginx

echo -e "\n>>> Copying NGINX config"
cp /srv/infra/nginx/nginx.conf /etc/nginx/nginx.conf
rm -f /etc/nginx/sites-enabled/default
cp /srv/infra/nginx/website.conf /etc/nginx/sites-enabled/

echo -e "\n>>> Testing NGINX config"
nginx -t

echo -e "\n>>> Reloading NGINX config"
nginx -s reload

echo -e "\n>>> Finished installing NGINX"
