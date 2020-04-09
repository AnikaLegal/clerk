import logging

import requests
from django.conf import settings

from questions.models import Submission

logger = logging.getLogger(__name__)

NOEL_USER_ID = "U9PMDQ665"
ALEX_USER_ID = "UMMPBKKNH"
HEADERS = {"Content-Type": "application/json"}


def send_submission_slack(submission_pk: str):
    url = settings.SUBMIT_SLACK_WEBHOOK_URL
    submission = Submission.objects.get(pk=submission_pk)
    text = get_text(submission)
    logging.info("Notifying Slack of Submission<%s>", submission_pk)
    requests.post(url, json={"text": text}, headers=HEADERS)


def get_text(submission: Submission):
    return f"""Hi <@{ALEX_USER_ID}> and <@{NOEL_USER_ID}>.

A client has just submitted their {submission.topic} questionnaire answers for review.
Their submission id is {submission.pk}.
Check your email at webmaster@anikalegal.com

:heart: Client Bot :robot_face:
"""
