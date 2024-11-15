from .base import *

SUBMISSION_EMAILS = ["test@example.com"]

DEBUG = False
EMAIL_PREFIX = "TEST"
SECRET_KEY = "test-secret-key"
ALLOWED_HOSTS = ["*"]
DATABASES["default"]["name"] = "test"
MEDIA_ROOT = os.path.join(BASE_DIR, "test_media")

FILE_UPLOAD_STORAGE = "default"

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        # Use default, otherwise Whitenoise gets angry and fails to load static files.
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
    },
}

# Django-q cluster should run synchronously
Q_CLUSTER = {
    "name": "clerk",
    "sync": True,  # tasks run in sync
    "timeout": 60,  # seconds, tasks will be killed if they run for longer than this.
    "retry": 120,  # seconds, time until retry
    "save_limit": 250,  # number of tasks saved to broker
    "orm": "default",  # Use Django's ORM + database for broker
}


EMAIL_DOMAIN = "fake.anikalegal.com"

# Reminder emails via MailChimp
MAILCHIMP_COVID_LIST_ID = ""
MAILCHIMP_COVID_WORKFLOW_ID = ""
MAILCHIMP_COVID_EMAIL_ID = ""
MAILCHIMP_REPAIRS_LIST_ID = ""
MAILCHIMP_REPAIRS_WORKFLOW_ID = ""
MAILCHIMP_REPAIRS_EMAIL_ID = ""

# MS Graph Integration
CASES_FOLDER_ID = "014GE5DG2XPLXZF3NLYNGK4IDSYOAG5ICE"

CLERK_BASE_URL = "http://localhost:8000"

SLACK_MESSAGE_DISABLED = True

# Ensure no access to API secrets in tests (even in dev container).
AWS_S3_ACCESS_KEY_ID = None
AWS_S3_SECRET_ACCESS_KEY = None
AZURE_AD_CLIENT_ID = None
AZURE_AD_CLIENT_SECRET = None
EMAIL_HOST_PASSWORD = None
MAILCHIMP_API_KEY = None
SENDGRID_API_KEY = None
SENTRY_JS_DSN = None
SLACK_API_TOKEN = None
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = None
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = None
TWILIO_ACCOUNT_SID = None
TWILIO_AUTH_TOKEN = None
