# Use Clerk base image
FROM anikalaw/clerkbase:latest

# Install Python packages
COPY app/requirements.txt .
RUN \
  echo "Installing python packages..." && \
  pip install -r requirements.txt

# Mount the codebase
ADD app /app

# Collect static files
ARG DJANGO_SETTINGS_MODULE=clerk.settings.prod
ARG DJANGO_SECRET_KEY=not-a-secret
ARG ACTIONSTEP_CLIENT_ID=not-the-id
ARG ACTIONSTEP_CLIENT_SECRET=not-the-secret
ARG MAILCHIMP_API_KEY=not-the-key
RUN mkdir -p /static/ && python3 ./manage.py collectstatic --noinput
