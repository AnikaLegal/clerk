# The Clerk base image (docker/Dockerfile.base), by dated tag rather than a
# moving one: a build can otherwise keep using a months-old local copy without
# noticing. Bump this and run `just push-base` when the base changes.
ARG BASE_TAG=2026-09-17

# Build web CSS assets
FROM node:24-slim AS web-builder
WORKDIR /web
COPY app/web/package.json .
COPY app/web/package-lock.json .
RUN echo "Installing Node modules." && \
    npm ci --silent
COPY app/web /web
RUN echo "Building web assets" && \
    npm run build

# Build the Clerk frontend here rather than copying it out of another image, so
# that this image builds on its own, from a checkout alone. The dev server runs
# on the frontend-deps stage (see the build-frontend recipe in the justfile), so
# both use the same Node and the same install.
FROM node:24-slim AS frontend-deps
WORKDIR /frontend
COPY frontend/package.json .
COPY frontend/package-lock.json .
RUN echo "Installing Node modules." && \
    npm ci --silent
COPY frontend /frontend

FROM frontend-deps AS frontend-builder
RUN echo "Building frontend" && \
    npm run build

# The public intake form, built the same way. The dev server runs on the
# intake-deps stage (see the build-intake recipe in the justfile). The build
# runs the tests first so a broken flow cannot ship.
FROM node:24-slim AS intake-deps
WORKDIR /intake
COPY intake/package.json .
COPY intake/package-lock.json .
RUN echo "Installing Node modules." && \
    npm ci --silent
COPY intake /intake

FROM intake-deps AS intake-builder
RUN echo "Testing intake" && \
    npm run test
RUN echo "Building intake" && \
    npm run build

# Use Clerk base image
FROM anikalaw/clerkbase:${BASE_TAG}
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
# Build on a uv-managed interpreter rather than whichever python3 the base
# image happens to carry, so the version is the same here as in a local venv
# and does not move when the base image is rebuilt.
ENV UV_PYTHON_PREFERENCE=only-managed

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

# Copy the built assets. The intake build lives in its own subdirectory so its
# manifest.json and assets don't collide with the frontend build's.
COPY --from=frontend-builder /frontend/dist/ /dist/
COPY --from=intake-builder /intake/dist/ /dist/intake/
COPY --from=web-builder /dist/web/ /dist/web/

# Collect static files
RUN ./manage.py collectstatic --noinput
