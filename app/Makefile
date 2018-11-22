# Allows us to run several commands in one bash shelll
.ONESHELL:

# Run webpack for local development
webpack:
	cd frontend
	yarn develop

# Run Django website for local development
web-local:
	./manage.py runserver 0.0.0.0:8000

# Lint frontend and backend code
lint:
	cd frontend
	yarn lint
	# TODO flake8 + isort

# Auto-format frontend and backend code
format:
	cd frontend
	yarn format
	# TODO isort
