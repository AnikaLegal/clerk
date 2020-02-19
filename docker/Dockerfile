# Use Clerk base image
FROM anikalaw/clerkbase:latest

# Install PDF kit binary
# https://github.com/JazzCore/python-pdfkit/blob/master/travis/before-script.sh
ENV WKHTML2PDF_VERSION 0.12.4
RUN apt-get install -y openssl build-essential xorg libssl-dev
RUN wget "https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/${WKHTML2PDF_VERSION}/wkhtmltox-${WKHTML2PDF_VERSION}_linux-generic-amd64.tar.xz"
RUN tar -xJf "wkhtmltox-${WKHTML2PDF_VERSION}_linux-generic-amd64.tar.xz"
RUN chown root:root wkhtmltox/bin/wkhtmltopdf
RUN cp -r wkhtmltox/* /usr/

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
RUN mkdir -p /static/ && ./manage.py collectstatic --noinput
