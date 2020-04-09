# flake8: noqa
from . import *

DEBUG = True
SECRET_KEY = "its-a-secret-key!"

EMAIL_PREFIX = "DEV"
MATT_EMAIL = "matt@anikalegal.com"
SUBMISSION_EMAILS = [MATT_EMAIL]

ALLOWED_HOSTS = ["*"]
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_REGEX_WHITELIST = (r"^(https?://)?(localhost|127\.0\.0\.1|0\.0\.0\.0)(:\d{4})?$",)
AWS_STORAGE_BUCKET_NAME = "anika-clerk-test"


SUBMIT_SLACK_WEBHOOK_URL = MATTSEGAL_SUBMIT_SLACK_WEBHOOK_URL
