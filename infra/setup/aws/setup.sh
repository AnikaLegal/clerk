if ! command -v aws &> /dev/null
then
    echo -e "\n>>> Installing AWS CLI"
    apt-get install --yes unzip

    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "/tmp/awscliv2.zip"
    unzip /tmp/awscliv2.zip
    /tmp/aws/install --bin-dir /usr/local/bin --install-dir /usr/local/aws-cli --update
    rm /tmp/awscliv2.zip
    rm -rf /tmp/aws
else
    echo -e "\n>>> AWS CLI already installed"
fi

echo -e "\n>>> Finished installing AWS CLI"
