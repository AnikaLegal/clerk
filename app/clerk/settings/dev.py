# flake8: noqa
from . import *

DEBUG = True
SECRET_KEY = "its-a-secret-key!"

EMAIL_PREFIX = "DEV"
MATT_EMAIL = "matt@anikalegal.com"
SUBMISSION_EMAILS = [MATT_EMAIL]

ALLOWED_HOSTS = ["*"]
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_REGEX_WHITELIST = (
    r"^(https?://)?(localhost|127\.0\.0\.1|0\.0\.0\.0)(:\d{4})?$",
)
AWS_STORAGE_BUCKET_NAME = "anika-clerk-test"

ACTIONSTEP_REDIRECT_URI = "http://localhost:8000/actionstep/end/"
ACTIONSTEP_WEB_URI = "https://ap-southeast-2.actionstepstaging.com"
ACTIONSTEP_OAUTH_URI = "https://go.actionstepstaging.com"
ACTIONSTEP_TOKEN_URI = "https://api.actionstepstaging.com"
ACTIONSTEP_SETUP_OWNERS = {
    "REPAIRS": "matt@anikalegal.com",
    "RENT_REDUCTION": "matt@anikalegal.com",
    "OTHER": "matt@anikalegal.com",
}

ADMIN_PREFIX = "local"

# Reminder emails via MailChimp
MAILCHIMP_API_KEY = os.environ["MAILCHIMP_API_KEY"]
MAILCHIMP_COVID_LIST_ID = "c24dfd19c4"
MAILCHIMP_COVID_WORKFLOW_ID = "53dfbbcabe"
MAILCHIMP_COVID_EMAIL_ID = "2192f4261c"
MAILCHIMP_REPAIRS_LIST_ID = "c24dfd19c4"
MAILCHIMP_REPAIRS_WORKFLOW_ID = "53dfbbcabe"
MAILCHIMP_REPAIRS_EMAIL_ID = "2192f4261c"
