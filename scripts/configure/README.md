# Clerk Configuration Managment

This folder contains Ansible scripts which configure the Clerk web server.

A single AWS EC2 server runs:

- NGINX server
- Postgres database
- Docker swarm

### Getting Started

```bash
virtualenv -p python3 ~/.venv
. ~/.venv/bin/activate
pip3 install -r requirements.txt
```
### Docker Swarm

Docker swarm hosts the application containers as 'stacks', generated from a docker-compose file. Web containers expose a static port for NGINX.

You need to manually init the swarm using

```
docker swarm init
```

### NGINX

NGINX is installed on the host server. It uses static port mapping to route requests to containers.

To flush your local DNS cache

    sudo /etc/init.d/dns-clean restart
    sudo /etc/init.d/networking force-reload

### Database:

Postgres is installed on the host server. Each service has its own database.

To acces psql

    su - postgres
    psql


## Ansible

Ansible config lives in `ansible/`

Ansible currently configures postgres and NGINX on the host server.

To encrypt secrets:

    ./encrypt-secrets.sh

To configure the docker host VM with secrets

    ./configure.sh
