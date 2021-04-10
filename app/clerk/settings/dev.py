# flake8: noqa
from . import *

DEBUG = True
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

# Call Centre powered by Twilio
TWILIO_PHONE_NUMBER = "+61480015687"
TWILIO_AUDIO_BASE_URL = "https://anika-twilio-audio-test.s3-ap-southeast-2.amazonaws.com"


ACTIONSTEP_REDIRECT_URI = "http://localhost:8000/actionstep/end/"
ACTIONSTEP_WEB_URI = "https://ap-southeast-2.actionstep.com"
ACTIONSTEP_OAUTH_URI = "https://go.actionstep.com"
ACTIONSTEP_TOKEN_URI = "https://api.actionstep.com"
ACTIONSTEP_SETUP_OWNER = "coordinators@anikalegal.com"
