# Use Clerk base image
FROM anikalaw/clerkbase:latest

# Install Python packages
COPY app/requirements.txt .
RUN \
  echo "Installing python packages..." && \
  pip install -r requirements.txt


# Install JavaScript packages
COPY app/frontend/package.json /app/frontend/package.json
COPY app/frontend/package-lock.json /app/frontend/package-lock.json
WORKDIR /app/frontend
RUN \
  echo "Installing JavaScript packages..." && \
  npm install

RUN \
  echo "Running Webpack..." && \
  npm run prod

# Mount the codebase
WORKDIR /app
ADD app /app

# Collect static files
ARG DJANGO_SETTINGS_MODULE=clerk.settings.prod
ARG DJANGO_SECRET_KEY=not-a-secret
ARG ACTIONSTEP_CLIENT_ID=not-the-id
ARG ACTIONSTEP_CLIENT_SECRET=not-the-secret
ARG MAILCHIMP_API_KEY=not-the-key
ARG TWILIO_ACCOUNT_SID=not-the-id
ARG TWILIO_AUTH_TOKEN=not-the-token
ARG AZURE_AD_CLIENT_ID=not-the-id
ARG AZURE_AD_CLIENT_SECRET=not-the-secret
RUN mkdir -p /static/ && python3 ./manage.py collectstatic --noinput
