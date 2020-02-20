import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

NOEL_USER_ID = "U9PMDQ665"
ALEX_USER_ID = "UMMPBKKNH"
HEADERS = {"Content-Type": "application/json"}


def send_submission_slack(submission_pk):
    url = settings.SUBMIT_SLACK_WEBHOOK_URL
    text = get_text(submission_pk)
    if url:
        logging.info("Notifying slack of Submission<%s>", submission_pk)
        requests.post(url, json={"text": text}, headers=HEADERS)
    else:
        logging.info(
            "Not notifying slack of Submission<%s>, no URL provided", submission_pk
        )


def get_text(submission_pk):
    return f"""Hi <@{ALEX_USER_ID}> and <@{NOEL_USER_ID}>.

A client has just submitted their questionnaire answers for review.
Their submission id is {submission_pk}.
Check your email at webmaster@anikalegal.com

:heart: Client Bot :robot_face:
"""
