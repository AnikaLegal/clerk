# Allows us to run several commands in one bash shelll
.ONESHELL:


# Run webpack for local development
webpack:
	cd frontend
	yarn develop


# Run Django website for local development
web-local:
	./manage.py runserver 0.0.0.0:8000


# Lint frontend and Python code
lint: lint-python lint-frontend


# Lint Python code
lint-python:
	flake8 \
		--max-line-length=120 \
		--exclude='*migrations*,/app/frontend' \
		.
	isort \
		-l 120 \
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
	isort \
		-l 120 \
		--skip migrations --skip /app/frontend
	black \
		--line-length 120 \
		--exclude "frontend/|migrations/" \
		--skip-string-normalization \
		.
