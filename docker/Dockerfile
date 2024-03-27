# Use Clerk base image
FROM anikalaw/clerkbase:latest
ARG DJANGO_SETTINGS_MODULE=clerk.settings.prod
ARG DJANGO_SECRET_KEY=not-a-secret
ENV PATH="/root/.local/bin:${PATH}"

# Mount the codebase
ADD app /app

# Install Python packages
RUN \
  echo "Installing python packages..." && \
  poetry install --no-root --no-interaction --no-ansi

# Copy Webpack prod build artifacts from clerk-webpack image
COPY --from=clerk-webpack:local /build /build

# Collect static files
RUN mkdir -p /static/ && python3 ./manage.py collectstatic --noinput
