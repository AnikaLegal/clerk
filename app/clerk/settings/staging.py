# flake8: noqa
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from .base import *

ENVIRONMENT = "staging"
DEBUG = False
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
ALLOWED_HOSTS = [
    "test.anikalegal.com",
    "test-clerk.anikalegal.com",  # TODO: Remove
    "127.0.0.1",
    "localhost",
]

EMAIL_PREFIX = "TEST"
WEBMASTER_EMAIL = "webmaster@anikalegal.com"
SUBMISSION_EMAILS = [WEBMASTER_EMAIL]

SESSION_COOKIE_DOMAIN = ".anikalegal.com"
SESSION_SAVE_EVERY_REQUEST = True
CSRF_COOKIE_DOMAIN = ".anikalegal.com"
CSRF_TRUSTED_ORIGINS = ["https://*.anikalegal.com"]
CORS_ORIGIN_ALLOW_ALL = False
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_REGEX_WHITELIST = (
    r"^(https?://)?(\w*-*\w*\.+)*anikalegal\.com$",
    r"^(https?://)?(localhost|127\.0\.0\.1|0\.0\.0\.0)(:\d{4})?$",
)

# Get DRF to use HTTPS in links.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

AWS_STORAGE_BUCKET_NAME = "anika-clerk-test"


# Sentry
sentry_sdk.init(
    dsn=os.environ.get("RAVEN_DSN"),
    integrations=[DjangoIntegration()],
    environment=ENVIRONMENT,
)


ADMIN_PREFIX = "staging"

# Reminder emails via MailChimp
MAILCHIMP_COVID_LIST_ID = "9749f1f08c"
MAILCHIMP_COVID_WORKFLOW_ID = "fb4daa69fe"
MAILCHIMP_COVID_EMAIL_ID = "e8ae8c5b35"
MAILCHIMP_REPAIRS_LIST_ID = "aa24ab1b75"
MAILCHIMP_REPAIRS_WORKFLOW_ID = "3bd9c82043"
MAILCHIMP_REPAIRS_EMAIL_ID = "04fb17ccee"

# Transactional emails via SendGrid
EMAIL_DOMAIN = "em7221.test-mail.anikalegal.com"
EMAIL_BUCKET_NAME = "anika-emails-test"
INTAKE_NOEMAIL_EMAIL = "tech@anikalegal.com"

# Call Centre powered by Twilio
TWILIO_PHONE_NUMBER = "+61480015687"
TWILIO_AUDIO_BUCKET_NAME = "anika-twilio-audio-test"

SOCIAL_AUTH_REDIRECT_IS_HTTPS = True

# Google Analytics
GOOGLE_ANALYTICS_ID = "G-ZVV8S5CGHZ"

# MS Graph Integration
MS_GRAPH_GROUP_ID = "4d0ce3f7-cec0-478b-aae8-1d981c2aede2"
MS_GRAPH_DRIVE_ID = "b!zBUQNn3jdEO44jZXmI-2GO0Krjc71QFLkmFqmCjMqFZZhq6ZPsfjR6HYQBbAK0_E"
CASES_FOLDER_ID = "012MW3H5PFZKSKCYCV4ZH25IDR5GUXGAJC"

CLERK_BASE_URL = "https://test.anikalegal.com"
WAGTAILADMIN_BASE_URL = CLERK_BASE_URL
