# Build web CSS assets
FROM node:lts-slim AS css-builder
WORKDIR /web
COPY app/web/package.json .
COPY app/web/package-lock.json .
RUN echo "Installing Node modules." && \
    npm install --silent
ADD app/web /web
RUN echo "Building CSS" && \ 
    mkdir /dist && \
    npx @tailwindcss/cli -i src/input.css -o /dist/daisyui.css

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

# Copy frontend build assets (for production only)
COPY --from=clerk-frontend:local /frontend/dist/ /dist/
COPY --from=css-builder /dist/daisyui.css /dist/web/styles/daisyui.css

# Collect static files
RUN ./manage.py collectstatic --noinput