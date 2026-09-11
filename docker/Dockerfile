# Build web CSS assets
FROM node:lts-slim AS web-builder
WORKDIR /web
COPY app/web/package.json .
COPY app/web/package-lock.json .
RUN echo "Installing Node modules." && \
    npm ci --silent
ADD app/web /web
RUN echo "Building web assets" && \
    npm run build

# Use Clerk base image
FROM anikalaw/clerkbase:latest
ARG DJANGO_SETTINGS_MODULE=clerk.settings.prod
ARG DJANGO_SECRET_KEY=not-a-secret
# Keep the virtualenv outside /app so that the local dev bind mount of the app
# source does not shadow it (see docker/docker-compose.local.yml).
ENV UV_PROJECT_ENVIRONMENT=/venv
ENV PATH="/venv/bin:${PATH}"
# The uv cache is a build cache mount rather than part of the image, so
# packages must be copied into the venv (hardlinks cannot cross the mount).
ENV UV_LINK_MODE=copy
ENV UV_COMPILE_BYTECODE=1

# Install python executable & dependencies from the lockfile alone so this
# layer only rebuilds when dependencies change, not on every source edit.
# uv is mounted temporarily as it is not needed in the final image.
COPY app/pyproject.toml app/uv.lock /app/
RUN --mount=from=ghcr.io/astral-sh/uv:0.12,source=/uv,target=/bin/uv \
    --mount=type=cache,target=/root/.cache/uv \
    echo "Installing python executable & dependencies..." && \
    uv sync --frozen --no-install-project

# Mount the codebase
COPY app /app

# Copy frontend build assets (for production only)
COPY --from=clerk-frontend:local /frontend/dist/ /dist/
COPY --from=web-builder /dist/web/ /dist/web/

# Collect static files
RUN ./manage.py collectstatic --noinput
