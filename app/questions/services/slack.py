import logging

import requests
from django.conf import settings

from questions.models import Submission

logger = logging.getLogger(__name__)


def send_submission_slack(submission_pk: str):
    url = settings.SUBMIT_SLACK_WEBHOOK_URL
    submission = Submission.objects.get(pk=submission_pk)
    text = get_text(submission)
    logging.info("Notifying Slack of Submission<%s>", submission_pk)
    resp = requests.post(url, json={"text": text}, headers={"Content-Type": "application/json"})
    resp.raise_for_status()
    # Mark request as sent
    Submission.objects.filter(pk=submission.pk).update(is_alert_sent=True)


def get_text(submission: Submission):
    return f"""Hi <@{settings.SLACK_USER.ALEX}>.

A client has just submitted their {submission.topic} questionnaire answers for review.
Their submission id is {submission.pk}.
Check your email at webmaster@anikalegal.com

:heart: Client Bot :robot_face:
"""
