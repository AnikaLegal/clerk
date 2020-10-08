#
# This Makefile contains commands which are run by developers, outside of Docker.
# Most of these commands use the Makefile at ./app/Makefile
#
# If you find yourself running the same docker-compose command over and over,
# then consider adding it here.
#
# Build local Docker envrionment
build:
	docker build . --tag clerk:local -f docker/Dockerfile

# Run Django website for local development
web:
	docker-compose -f docker/docker-compose.local.yml up web

# Run Django reporting server for local development
streamlit:
	docker-compose -f docker/docker-compose.local.yml up streamlit

# Run Django with debugging enabled
debug:
	docker-compose -f docker/docker-compose.local.yml run --rm --service-ports web

# Get a bash shell in the docker container
bash:
	docker-compose -f docker/docker-compose.local.yml run --rm web bash

# Get a Django shell_plus shell in the docker container
shell:
	docker-compose -f docker/docker-compose.local.yml run --rm web make shell

# Get a Postgres shell in the docker container
psql:
	docker-compose -f docker/docker-compose.local.yml run --rm web psql

# Lint Python code
lint:
	docker-compose -f docker/docker-compose.local.yml run --rm test make lint

# Auto-format frontend and backend code
format:
	docker-compose -f docker/docker-compose.local.yml run --rm test make format

# Run PyTest
test:
	docker-compose -f docker/docker-compose.local.yml run --rm test make test

# View worker logs
logs:
	docker-compose -f docker/docker-compose.local.yml logs --tail 100 -f worker 
