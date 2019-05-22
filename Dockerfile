# Use Clerk base image
FROM anikalaw/clerkbase:latest

# Install Python packages
COPY app/requirements.txt .
RUN \
  echo "Installing python packages..." && \
  pip3 install -r requirements.txt


# Mount the codebase
ADD app /app
