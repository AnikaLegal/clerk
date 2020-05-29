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
    "COVID": "matt@anikalegal.com",
}
