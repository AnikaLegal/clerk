# flake8: noqa
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from . import *

DEBUG = False
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
ALLOWED_HOSTS = ["test-clerk.anikalegal.com", "127.0.0.1", "localhost"]

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

ACTIONSTEP_REDIRECT_URI = "https://test-clerk.anikalegal.com/actionstep/end/"
ACTIONSTEP_WEB_URI = "https://ap-southeast-2.actionstepstaging.com"
ACTIONSTEP_OAUTH_URI = "https://go.actionstepstaging.com"
ACTIONSTEP_TOKEN_URI = "https://api.actionstepstaging.com"
ACTIONSTEP_SETUP_OWNERS = {
    "REPAIRS": "matt@anikalegal.com",
    "COVID": "matt@anikalegal.com",
}
