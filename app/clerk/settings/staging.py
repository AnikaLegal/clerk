# flake8: noqa
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from . import *

DEBUG = False
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
ALLOWED_HOSTS = [
    "test-clerk.anikalegal.com",
    "test-reports.anikalegal.com",
    "127.0.0.1",
    "localhost",
]

EMAIL_PREFIX = "TEST"
WEBMASTER_EMAIL = "webmaster@anikalegal.com"
SUBMISSION_EMAILS = [WEBMASTER_EMAIL]

SESSION_COOKIE_DOMAIN = ".anikalegal.com"
SESSION_SAVE_EVERY_REQUEST = True
CSRF_COOKIE_DOMAIN = ".anikalegal.com"
CSRF_TRUSTED_ORIGINS = [".anikalegal.com"]
CORS_ORIGIN_ALLOW_ALL = False
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_REGEX_WHITELIST = (
    r"^(https?://)?(\w*-*\w*\.+)*anikalegal\.com$",
    r"^(https?://)?(localhost|127\.0\.0\.1|0\.0\.0\.0)(:\d{4})?$",
)

# Get DRF to use HTTPS in links.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

AWS_STORAGE_BUCKET_NAME = "anika-clerk-test"


sentry_sdk.init(
    dsn=os.environ.get("RAVEN_DSN"),
    integrations=[DjangoIntegration()],
    environment="test",
)


ADMIN_PREFIX = "staging"

# Reminder emails via MailChimp
MAILCHIMP_API_KEY = os.environ["MAILCHIMP_API_KEY"]
<<<<<<< HEAD
MAILCHIMP_COVID_LIST_ID = "9749f1f08c"
MAILCHIMP_COVID_WORKFLOW_ID = "fb4daa69fe"
MAILCHIMP_COVID_EMAIL_ID = "e8ae8c5b35"
MAILCHIMP_REPAIRS_LIST_ID = "aa24ab1b75"
MAILCHIMP_REPAIRS_WORKFLOW_ID = "3bd9c82043"
MAILCHIMP_REPAIRS_EMAIL_ID = "04fb17ccee"
=======
MAILCHIMP_COVID_LIST_ID = "c24dfd19c4"
MAILCHIMP_COVID_WORKFLOW_ID = "53dfbbcabe"
MAILCHIMP_COVID_EMAIL_ID = "2192f4261c"
MAILCHIMP_REPAIRS_LIST_ID = "c24dfd19c4"
MAILCHIMP_REPAIRS_WORKFLOW_ID = "53dfbbcabe"
MAILCHIMP_REPAIRS_EMAIL_ID = "2192f4261c"

# Call Centre powered by Twilio
TWILIO_ACCOUNT_SID = os.environ["TWILIO_ACCOUNT_SID"]
TWILIO_AUTH_TOKEN = os.environ["TWILIO_AUTH_TOKEN"]
>>>>>>> Make twilio env vars available in web container for staging and prod
