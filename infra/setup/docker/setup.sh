set -e

if ! command -v docker &> /dev/null
then
    echo -e "\n>>> Installing Docker"
    apt-get install --yes docker.io

    echo -e "\n>>> Enabling Docker Swarm"
    docker swarm init
else
    echo -e "\n>>> Docker already installed"
fi
