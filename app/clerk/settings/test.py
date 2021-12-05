from .base import *

SUBMISSION_EMAILS = ["test@example.com"]

DEBUG = False
EMAIL_PREFIX = "TEST"
SECRET_KEY = "test-secret-key"
ALLOWED_HOSTS = ["*"]
DATABASES["default"]["name"] = "test"
DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
MEDIA_ROOT = os.path.join(BASE_DIR, "test_media")

# Use default, otherwise Whitenoise gets angry and fails to load static files.
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# Django-q cluster should run synchronously
Q_CLUSTER = {
    "name": "clerk",
    "sync": True,  # tasks run in sync
    "timeout": 60,  # seconds, tasks will be killed if they run for longer than this.
    "retry": 120,  # seconds, time until retry
    "save_limit": 250,  # number of tasks saved to broker
    "orm": "default",  # Use Django's ORM + database for broker
}

ACTIONSTEP_SYNC = True
ACTIONSTEP_SETUP_OWNER = "keithleonardo@anikalegal.com"
ACTIONSTEP_WEB_URI = "https://example.com"

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