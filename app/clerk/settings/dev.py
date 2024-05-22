# flake8: noqa
import socket
from .base import *

DEBUG = True

# Django debug toolbar + Docker setup
hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
INTERNAL_IPS = [ip[:-1] + "1" for ip in ips] + ["127.0.0.1", "10.0.2.2"]

SECRET_KEY = "its-a-secret-key!"

EMAIL_PREFIX = "DEV"
MATT_EMAIL = "matt@anikalegal.com"
SUBMISSION_EMAILS = [MATT_EMAIL]

ALLOWED_HOSTS = ["*"]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = True

AWS_STORAGE_BUCKET_NAME = "anika-clerk-test"

ADMIN_PREFIX = "local"

# Reminder emails via MailChimp
MAILCHIMP_COVID_LIST_ID = "9749f1f08c"
MAILCHIMP_COVID_WORKFLOW_ID = "fb4daa69fe"
MAILCHIMP_COVID_EMAIL_ID = "e8ae8c5b35"
MAILCHIMP_REPAIRS_LIST_ID = "aa24ab1b75"
MAILCHIMP_REPAIRS_WORKFLOW_ID = "3bd9c82043"
MAILCHIMP_REPAIRS_EMAIL_ID = "04fb17ccee"

# Transactional emails via SendGrid
EMAIL_DOMAIN = "em9463.dev-mail.anikalegal.com"
INTAKE_NOEMAIL_EMAIL = "tech@anikalegal.com"

# Call Centre powered by Twilio
TWILIO_PHONE_NUMBER = "+61480015687"
TWILIO_AUDIO_BUCKET_NAME = "anika-twilio-audio-test"

# MS Graph Integration
MS_GRAPH_GROUP_ID = "d6b81121-9482-45d4-9acd-6fa42111d5b3"
MS_GRAPH_DRIVE_ID = "b!Byhxuh0t_ESbqiHJZpNyHbsJLbi6tCpKomnhyRvhq7L3St3-kEDdTq9Ft70M4eXu"
CASES_FOLDER_ID = "014GE5DG2XPLXZF3NLYNGK4IDSYOAG5ICE"


CLERK_BASE_URL = "http://localhost:8000"

WEBPACK_LOADER["DEFAULT"]["CACHE"] = False
