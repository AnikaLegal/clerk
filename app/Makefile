#
# This Makefile contains commands which are run inside the Docker containers,
# I do not recommend invoking these directly - see Makefile at project root instead.
#
# Allows us to run several commands in one bash shelll
.ONESHELL:

web-local:
	./manage.py runserver 0.0.0.0:8000

# Run Django website using gunicorn production
web-prod:
	echo "Starting clerk app as `whoami`" && \
	echo "Starting remote syslog" && \
	mkdir -p /var/log/gunicorn && \
	touch /var/log/gunicorn/access.log && \
	touch /var/log/gunicorn/error.log && \
	remote_syslog \
	--hostname "${PAPERTRAIL_HOSTNAME}" \
	--dest-port "${PAPERTRAIL_PORT}" \
	--dest-host "${PAPERTRAIL_URL}" \
	--pid-file /var/run/remote_syslog.pid \
	/var/log/gunicorn/access.log \
	/var/log/gunicorn/error.log && \
	echo "Running migrations" && \
	./manage.py migrate && \
	echo "Starting gunicorn" && \
	gunicorn clerk.wsgi:application \
	--name clerk \
	--workers 2 \
	--bind 0.0.0.0:${GUNICORN_PORT} \
	--capture-output \
	--log-level info \
	--error-logfile /var/log/gunicorn/error.log \
	--access-logfile /var/log/gunicorn/access.log

# Lint Python code
lint:
	flake8 \
		--max-line-length=90 \
		--exclude='*migrations*,/app/frontend' \
		.
	isort \
		-l 90 \
		--diff \
		--check-only \
		--skip migrations --skip /app/frontend


# Auto-format Python code
format:
	black \
		--line-length 90 \
		--exclude "frontend/|migrations/" \
		--skip-string-normalization \
		.
	isort \
		-l 90 \
		--skip migrations --skip /app/frontend \
		--apply

# Run PyTest
test:
	export DJANGO_SETTINGS_MODULE=clerk.settings.test
	pytest -s -vv --reuse-db
