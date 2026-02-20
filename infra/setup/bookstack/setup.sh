# Install BookStack app on Ubuntu 18.04
# DO NOT TRY TO RUN THIS END TO END
# https://www.bookstackapp.com/docs/admin/installation/#ubuntu-1804
set -e

echo "Installed SSH keys:"
cat /home/ubuntu/.ssh/authorized_keys

# Download and run the BookStackApp setup script
DOMAIN="wiki.anikalegal.com"
SCRIPT_URL=https://raw.githubusercontent.com/BookStackApp/devops/master/scripts/installation-ubuntu-18.04.sh
wget $SCRIPT_URL
chmod a+x installation-ubuntu-18.04.sh
sudo ./installation-ubuntu-18.04.sh $DOMAIN


if [[ -z "$AWS_ACCESS_KEY_ID" ]]; then
    echo "Envar AWS_ACCESS_KEY_ID must be set"
    exit 1
fi
if [[ -z "$AWS_SECRET_ACCESS_KEY" ]]; then
    echo "Envar AWS_SECRET_ACCESS_KEY must be set"
    exit 1
fi

read -r -d '' STORAGE_CONFIG <<EOF

APP_URL=https://wiki.anikalegal.com

STORAGE_TYPE=s3
STORAGE_S3_KEY=$AWS_ACCESS_KEY_ID
STORAGE_S3_SECRET=$AWS_SECRET_ACCESS_KEY
STORAGE_S3_BUCKET=anika-bookstack
STORAGE_S3_REGION=ap-southeast-2
EOF
echo "$STORAGE_CONFIG" | sudo tee --append /var/www/bookstack/.env
sudo systemctl restart apache2
 