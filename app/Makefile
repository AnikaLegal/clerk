#
# This Makefile contains commands which are run inside the Docker containers,
# I do not recommend invoking these directly - see Makefile at project root instead.
#
# Allows us to run several commands in one bash shelll
.ONESHELL:


# Run webpack for local development
webpack:
	cd frontend
	yarn develop


# Run Django website for local development
web-local:
	./manage.py runserver 0.0.0.0:8000


# Run Django website using gunicorn production
web-prod:
	mkdir -p /var/log/gunicorn && \
	touch /var/log/gunicorn/access.log && \
	touch /var/log/gunicorn/error.log && \
	echo "Running migrations" && \
	./manage.py migrate && \
	echo "Starting gunicorn" && \
	gunicorn clerk.wsgi:application \
	--name clerk \
	--workers 2 \
	--bind 0.0.0.0:8000 \
	--capture-output \
	--log-level info \
	--error-logfile /var/log/gunicorn/error.log \
	--access-logfile /var/log/gunicorn/access.log


# Lint frontend and Python code
lint: lint-python lint-frontend


# Lint Python code
lint-python:
	flake8 \
		--max-line-length=90 \
		--exclude='*migrations*,/app/frontend' \
		.
	isort \
		-l 90 \
		--diff \
		--check-only \
		--skip migrations --skip /app/frontend


# Lint frontend code
lint-frontend:
	cd frontend
	yarn lint


# Auto-format frontend and backend code
format: format-python format-frontend


# Auto-format frontend code
format-frontend:
	cd frontend
	yarn format


# Auto-format Python code
format-python:
	black \
		--line-length 90 \
		--exclude "frontend/|migrations/" \
		--skip-string-normalization \
		.
	isort \
		-l 90 \
		--skip migrations --skip /app/frontend \
		--apply
