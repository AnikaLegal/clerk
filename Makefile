#
# This Makefile contains commands which are run by developers, outside of Docker.
# Most of these commands use the Makefile at ./app/Makefile
#
# If you find yourself running the same docker-compose command over and over,
# then consider adding it here.
#
# Run webpack for local development
webpack:
	docker-compose run --service-ports webpack

# Run Django website for local development
web:
	docker-compose up web

# Get a bash shell in the docker container
bash:
	docker-compose run web bash

# Get a Django shell_plus shell in the docker container
shell:
	docker-compose run web ./manage.py shell_plus

# Get a Postgres shell in the docker container
psql:
	docker-compose run web psql

# Lint frontend and Python code
lint:
	docker-compose run webpack make lint

# Lint Python code
lint-python:
	docker-compose run webpack make lint-python

# Lint frontend code
lint-frontend:
	docker-compose run webpack make lint-frontend

# Auto-format frontend and backend code
format:
	docker-compose run webpack make format

# Auto-format frontend code
format-frontend:
	docker-compose run webpack make format-frontend

# Auto-format Python code
format-python:
	docker-compose run webpack make format-python
