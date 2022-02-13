# Install BookStack app on Ubuntu 18.04
# DO NOT TRY TO RUN THIS END TO END
# https://www.bookstackapp.com/docs/admin/installation/#ubuntu-1804
set -e

# Add SSH keys
MS_DESKTOP_KEY="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCfXP53x8aMWUjml94SKFZTGP6IlRPakuYve0QPPWhR4e+UzWhBefNS5hl1eDLkfv4QhIx1ELelZgpHeqnOBNl2P79+p5Z/TFu5U66BbrRayVy2g7/mc5USfZw3D4jxRy+r7FVzUcdGs+S2yW1TW0PxMdzRrTvHXYAIq5ILgr4MBuzkhL4DTBXb4zD5Dlkeypeivi2gbrEA4LRnhas2xZULDVXPN7m/U4eVofHPERMTl23wX9iteYaIknoThS8pwyi2vGRj63bePV2l2GMw9KaG3IxoKLBqQkRori1u4WcZuuiMlgrEUfpqoZUBIon6LhsXAB4IzzaQwt7t+DLrFTckSLw6SNCkuXNuJmAPjeh4rsONies9NNZ72g++1ec4Yrh7SQK1GH/5EHU7g2qzR2Ygb0JkUmgwuvpc2L3mLg8daNV5mFaALcu03WiccnFkYu3qEcnIB+4YTNgHIClTJOaHENix3QJvyuFsESNE2nZUNDctKMNlVs/PD1Bq6sEeIqucZ4ONVzw1hXa2BLfym21nxRsccBLmQilVXsJfAnkd5+LkggfN8Mn0eYFM3M8w29HBcoZn2Gu6fdKD2hPjz+zDhzIik3HRidldZizUU0wj4uSEsBgZmd2vbI6+1ADJgAIAWZSqb093l7Qj1wtHUE3gaOhT8Nr8KkjxokMBKh2I7w== mattdsegal@gmail.com"
MS_LAPTOP_KEY="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCh+qrs9Z6nWX8kGnCWrOWHShjjPD3zPg5D78kn9jTBPz0yGBKoDvtkw390n1+opJjlRl8t9yCus1iHIw3IplGkRca5A6l5oCI+kXCH3iAgThleHbPcM+0tskT9ASmZTNVomfuipTlAap940kdUYYueJzRbNqUWFoN6hHf7AxLiIkAmTw8uFWw9ywJNydk81ETXN5xbPgtZW3rpdG/krH8HeV69bzygLN/SYDoQETBMW1AzGqpQI7TzJGfOwqDtLoTDQ6odYUvRQGcACg3DCDS/ZMNU2RgLPPvQSSLlMYV2QGI0e/YS82IkOqk79rByqCYVBQu9m7aPc206316WaWo/CTFFxF+0KTPuMF8uAtUOT3Iv6uOTtxQ6pcTgxC+jphKPDuJxebYui0dMgdJZa8ZIDduEzKcRChkfKRVGRDnyFCWFFeB3pj78teAwjyDRb3Y+o7nHxMQiNoCnRY31vdIYk/4DeBhiEtLmh7Ed8tzfo0chKqM1GXpffUy4G6RS+SYPYHVzgIKQsfzO4pKbROo669thiZ5MBMp1xKmupgZzM4nMy4Z8q3EyG22hwuAbUa9PnNcvoO8BKr2rupcot0ZhEWlHa6As5DrdUwdr3l1lKoy9f8+l9LojOxguEXddfTTUB5N022Pm6iyLdt9PByMyZvZrMlG2Q4UEhZqSDVe25w== mattdsegal@gmail.com"
echo $MS_DESKTOP_KEY >> /home/ubuntu/.ssh/authorized_keys
echo $MS_LAPTOP_KEY >> /home/ubuntu/.ssh/authorized_keys

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
 