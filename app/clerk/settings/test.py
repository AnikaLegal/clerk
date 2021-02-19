from . import *

SUBMISSION_EMAILS = ["test@example.com"]

DEBUG = False
EMAIL_PREFIX = "TEST"
SECRET_KEY = "test-secret-key"
ALLOWED_HOSTS = ["*"]
DATABASES["default"]["name"] = "test"
DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
MEDIA_ROOT = os.path.join(BASE_DIR, "test_media")

ACTIONSTEP_SETUP_OWNER = "keithleonardo@anikalegal.com"


# Django-q cluster should run synchronously
Q_CLUSTER = {
    "name": "clerk",
    "sync": True,  # tasks run in sync
    "timeout": 60,  # seconds, tasks will be killed if they run for longer than this.
    "retry": 120,  # seconds, time until retry
    "save_limit": 250,  # number of tasks saved to broker
    "orm": "default",  # Use Django's ORM + database for broker
}


ACTIONSTEP_WEB_URI = "https://example.com"

# Reminder emails via MailChimp
MAILCHIMP_COVID_LIST_ID = ""
MAILCHIMP_COVID_WORKFLOW_ID = ""
MAILCHIMP_COVID_EMAIL_ID = ""
MAILCHIMP_REPAIRS_LIST_ID = ""
MAILCHIMP_REPAIRS_WORKFLOW_ID = ""
MAILCHIMP_REPAIRS_EMAIL_ID = ""
