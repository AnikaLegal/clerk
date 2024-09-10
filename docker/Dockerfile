# Use Clerk base image
FROM anikalaw/clerkbase:latest
ARG DJANGO_SETTINGS_MODULE=clerk.settings.prod
ARG DJANGO_SECRET_KEY=not-a-secret
ENV PATH="/app/.venv/bin:${PATH}"

# Mount the codebase
ADD app /app

# Install python executable & dependencies. Note we use uv temporarily as it is
# not needed in the final image.
RUN --mount=from=ghcr.io/astral-sh/uv,source=/uv,target=/bin/uv \
    echo "Installing python executable & dependencies..." && \
    uv sync --frozen

# Copy Webpack prod build artifacts from clerk-webpack image
COPY --from=clerk-webpack:local /build /build

# Collect static files
RUN mkdir -p /static/ && ./manage.py collectstatic --noinput
