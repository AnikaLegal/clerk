"""
Django settings for clerk project.
"""
import os

DEBUG = False
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEFAULT_FROM_EMAIL = "noreply@anikalegal.com"
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    # Static files
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    # Dev tools
    "django_extensions",
    # APIs
    "rest_framework",
    "corsheaders",
    # Async tasks
    "django_q",
    # Internal apps
    "questions.apps.QuestionsConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "clerk.urls"

WSGI_APPLICATION = "clerk.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            # /app/templates/
            os.path.abspath(os.path.join(BASE_DIR, "..", "templates"))
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]


# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.environ.get("PGDATABASE"),
        "USER": os.environ.get("PGUSER"),
        "PASSWORD": os.environ.get("PGPASSWORD"),
        "HOST": os.environ.get("PGHOST"),
        "PORT": os.environ.get("PGPORT"),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Email backend
EMAIL_HOST = "smtp.sendgrid.net"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "apikey"
EMAIL_HOST_PASSWORD = os.environ.get("SENDGRID_API_KEY")

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Australia/Melbourne"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Enable iPython for shell_plus
SHELL_PLUS = "ipython"


# Static files
STATIC_URL = "/static/"
STATIC_ROOT = "/static/"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Media storage
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
AWS_S3_SECURE_URLS = False
AWS_QUERYSTRING_AUTH = False
AWS_DEFAULT_ACL = "public-read"
AWS_REGION_NAME = "ap-southeast-2"
AWS_S3_FILE_OVERWRITE = False  # Files with the same name will not each other
AWS_S3_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_S3_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")

# Disable CSRF
# FIXME: Remove this once users can log in and fetch a token - or if you figure out a smarter way to do this.
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.BasicAuthentication",
        "clerk.auth.CsrfExemptSessionAuthentication",
    )
}

Q_CLUSTER = {
    "name": "clerk",
    "timeout": 60,  # seconds,
    "retry": 60,  # seconds,
    "save_limit": 250,  # number of tasks saved to broker
    "orm": "default",  # Use Django's ORM + database for broker
}

# Adds a public slackbot notification to #general
PUBLIC_SUBMIT_SLACK_WEBHOOK_URL = os.environ.get("PUBLIC_SUBMIT_SLACK_WEBHOOK_URL")

# Add a private slackbot notification to @mattdsegal
PRIVATE_SUBMIT_SLACK_WEBHOOK_URL = os.environ.get("PRIVATE_SUBMIT_SLACK_WEBHOOK_URL")

# The URL the actually gets used
SUBMIT_SLACK_WEBHOOK_URL = None
