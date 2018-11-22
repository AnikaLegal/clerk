# Use Clerk base image
FROM anikalaw/clerkbase:latest

# Install Python packages
COPY app/requirements.txt .
RUN \
  echo "Installing python packages..." && \
  pip3 install -r requirements.txt

# Install Node packages
WORKDIR /app/frontend
COPY app/frontend/package.json .
COPY app/frontend/yarn.lock .
RUN yarn install
WORKDIR /app

# Mount the codebase
ADD app /app

# Run frontend build
#RUN yarn build

# Run staticfiles
#ARG DJANGO_SETTINGS_MODULE=clerk.settings.prod
#ARG DJANGO_SECRET_KEY=not-a-secret
#RUN mkdir -p /static/ && ./manage.py collectstatic --noinput
