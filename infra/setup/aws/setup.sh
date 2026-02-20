set -e

if ! command -v aws &> /dev/null
then
    echo -e "\n>>> Installing AWS CLI"
    apt-get install --yes unzip
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "/opt/awscliv2.zip"
    unzip /opt/awscliv2.zip -d /opt/
    rm /opt/awscliv2.zip
    /opt/aws/install
else
    echo -e "\n>>> AWS CLI already installed"
fi

echo -e "\n>>> Finished installing AWS CLI"
