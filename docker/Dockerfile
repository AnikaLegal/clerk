# Use Clerk base image
FROM anikalaw/clerkbase:latest


# Install Weasyprint dependencies
# https://weasyprint.readthedocs.io/en/stable/install.html#linux
RUN apt-get -qq update
RUN apt-get -qq install \
  build-essential \
  python3-wheel \
  python3-cffi \
  libcairo2 \
  libpango-1.0-0 \
  libpangocairo-1.0-0 \
  libgdk-pixbuf2.0-0 \
  libffi-dev \
  shared-mime-info

#
# Install Python packages
COPY app/requirements.txt .
RUN \
  echo "Installing python packages..." && \
  pip3 install -r requirements.txt

# Mount the codebase
ADD app /app

# Collect static files
ARG DJANGO_SETTINGS_MODULE=clerk.settings.prod
ARG DJANGO_SECRET_KEY=not-a-secret
ARG ACTIONSTEP_CLIENT_ID=not-the-id
ARG ACTIONSTEP_CLIENT_SECRET=not-the-secret
RUN mkdir -p /static/ && ./manage.py collectstatic --noinput
