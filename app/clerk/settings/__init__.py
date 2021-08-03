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
    "django.contrib.sitemaps",
    # Static files
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    # Dev tools
    "django_extensions",
    # APIs
    "rest_framework",
    "corsheaders",
    # Social auth
    "social_django",
    # Async tasks
    "django_q",
    # Internal apps
    "accounts.apps.AccountsConfig",
    "web.apps.WebConfig",
    "actionstep.apps.ActionstepConfig",
    "slack.apps.SlackConfig",
    "webhooks.apps.WebhooksConfig",
    "case.apps.CaseConfig",
    "core.apps.CoreConfig",
    "caller.apps.CallerConfig",
    "emails.apps.EmailsConfig",
    # Wagtail
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.contrib.modeladmin",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail.core",
    "modelcluster",
    "taggit",
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
    "social_django.middleware.SocialAuthExceptionMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
    "web.middleware.RedirectMiddleware",
]

ROOT_URLCONF = "clerk.urls"

WSGI_APPLICATION = "clerk.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]


# Database
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
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

# Authentication
AUTH_USER_MODEL = "accounts.User"
LOGIN_URL = "login"
LOGOUT_REDIRECT_URL = "login"
LOGIN_REDIRECT_URL = "case-list"
AUTHENTICATION_BACKENDS = [
    "social_core.backends.google.GoogleOAuth2",
    "django.contrib.auth.backends.ModelBackend",
]
SOCIAL_AUTH_JSONFIELD_ENABLED = True
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get("GOOGLE_OAUTH2_KEY")
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get("GOOGLE_OAUTH2_SECRET")
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]

SOCIAL_AUTH_GOOGLE_OAUTH2_WHITELISTED_DOMAINS = ["anikalegal.com"]

# See https://python-social-auth.readthedocs.io/en/latest/configuration/django.html
SOCIAL_AUTH_PIPELINE = (
    "social_core.pipeline.social_auth.social_details",
    "social_core.pipeline.social_auth.social_uid",
    "social_core.pipeline.social_auth.auth_allowed",
    "social_core.pipeline.social_auth.social_user",
    "social_core.pipeline.user.get_username",
    # Associates the current social details with another user account with a similar email address.
    "social_core.pipeline.social_auth.associate_by_email",
    "social_core.pipeline.user.create_user",
    "social_core.pipeline.social_auth.associate_user",
    "social_core.pipeline.social_auth.load_extra_data",
    "social_core.pipeline.user.user_details",
    # Ensure new users can access the Wagtail CMS
    "accounts.social_auth.set_new_user_as_cms_editor",
)
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

# Wagtail
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
WAGTAIL_SITE_NAME = "Anika Legal"

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

ONE_HUNDRED_YEARS = 100 * 365 * 24 * 60 * 60  # seconds
Q_CLUSTER = {
    "name": "clerk",
    "timeout": 60,  # seconds, tasks will be killed if they run for longer than this.
    # NB: Django-Q retries *forever*, tasks need to be manually deleted to stop this
    "retry": ONE_HUNDRED_YEARS,  # seconds, effectively never retry (this is a yucky hack.)
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
ACTIONSTEP_SETUP_OWNER = None
ACTIONSTEP_WEB_URI = None
ADMIN_PREFIX = None


# Call Centre powered by Twilio
TWILIO_ACCOUNT_SID = os.environ["TWILIO_ACCOUNT_SID"]
TWILIO_AUTH_TOKEN = os.environ["TWILIO_AUTH_TOKEN"]
TWILIO_PHONE_NUMBER = None  # Overwrite me
TWILIO_AUDIO_BASE_URL = None  # Overwrite me


# Transactional emails via SendGrid
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
EMAIL_HOST = "smtp.sendgrid.net"
EMAIL_HOST_USER = "apikey"
EMAIL_HOST_PASSWORD = SENDGRID_API_KEY
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_DOMAIN = "em7221.test-mail.anikalegal.com"


# Marketing emails via MailChimp
MAILCHIMP_API_KEY = os.environ["MAILCHIMP_API_KEY"]

# Analytics
GOOGLE_ANALYTICS_ID = ""
FACEBOOK_PIXEL_ID = ""


# MS Graph Integration
AZURE_AD_CLIENT_ID = os.environ["AZURE_AD_CLIENT_ID"]
AZURE_AD_CLIENT_SECRET = os.environ["AZURE_AD_CLIENT_SECRET"]
MS_AUTHORITY_URL = (
    "https://login.microsoftonline.com/e89f1fec-2d50-4795-886e-a3475bdc4e4b"
)
MS_GRAPH_GROUP_ID = "4d0ce3f7-cec0-478b-aae8-1d981c2aede2"
