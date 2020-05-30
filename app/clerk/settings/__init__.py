"""
Django settings for clerk project.
"""
import os

DEBUG = False
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEFAULT_FROM_EMAIL = "noreply@anikalegal.com"
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    # Custom admin
    "admin.apps.ClerkAdminConfig",
    # Django
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
    "actionstep.apps.ActionstepConfig",
    "slack.apps.SlackConfig",
    "webhooks.apps.WebhooksConfig",
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
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
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
AWS_S3_FILE_OVERWRITE = True  # Files with the same name will overwrite each other
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
    "timeout": 60,  # one minute.
    # NB: Django-Q retries *forever*, tasks need to be manually deleted to stop this
    "retry": 3600,  # an hour, must be longer than timeout
    "save_limit": 250,  # number of tasks saved to broker
    "orm": "default",  # Use Django's ORM + database for broker
}


# Everyone gets the same logging config
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "root": {"level": "INFO", "handlers": ["console", "file"]},
    "handlers": {
        "console": {"level": "INFO", "class": "logging.StreamHandler"},
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": "/var/log/django.log",
        },
    },
    "loggers": {
        "django": {"handlers": ["console", "file"], "level": "INFO", "propagate": True},
        "django.db.backends": {
            "level": "ERROR",
            "handlers": ["console", "file"],
            "propagate": False,
        },
    },
}


# Slack message types
class SlackMessage:
    ACTIONSTEP_CREATE = "actionstep-create"
    CLIENT_INTAKE = "client-intake"
    LANDING_FORM = "landing-form"


SLACK_MESSAGE = SlackMessage

ACTIONSTEP_CLIENT_ID = os.environ["ACTIONSTEP_CLIENT_ID"]
ACTIONSTEP_CLIENT_SECRET = os.environ["ACTIONSTEP_CLIENT_SECRET"]
ACTIONSTEP_SCOPES = [
    "filenotes",
    "users",
    "actions",
    "actioncreate",
    "participants",
    "actionparticipants",
    "participanttypes",
    "files",
    "actiondocuments",
    "actionfolders",
    "actiontypes",
]
# Override me!
ACTIONSTEP_REDIRECT_URI = None
ACTIONSTEP_OAUTH_URI = None
ACTIONSTEP_TOKEN_URI = None
ACTIONSTEP_SETUP_OWNERS = None
ACTIONSTEP_WEB_URI = None

STREAMLIT_BASE_URL = "http://3.106.55.74/streamlit-test/"


ADMIN_PREFIX = None
