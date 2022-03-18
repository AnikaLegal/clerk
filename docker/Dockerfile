# Use Clerk base image
FROM anikalaw/clerkbase:latest
ARG DJANGO_SETTINGS_MODULE=clerk.settings.prod
ARG DJANGO_SECRET_KEY=not-a-secret

# Install Python packages
COPY app/requirements.txt .
RUN \
  echo "Installing python packages..." && \
  pip install -r requirements.txt

# Mount the codebase
ADD app /app

# Copy Webpack prod build artifacts from clerk-webpack image
COPY --from=clerk-webpack:local /build /build

# Collect static files
RUN mkdir -p /static/ && python3 ./manage.py collectstatic --noinput
