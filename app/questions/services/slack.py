import logging

from django.conf import settings

from slack.services import send_slack_message
from questions.models import Submission

logger = logging.getLogger(__name__)


def send_submission_slack(submission_pk: str):
    submission = Submission.objects.get(pk=submission_pk)
    text = get_text(submission)
    logging.info("Notifying Slack of Submission<%s>", submission_pk)
    send_slack_message(settings.SLACK_MESSAGE.CLIENT_INTAKE, text)
    # Mark request as sent
    Submission.objects.filter(pk=submission.pk).update(is_alert_sent=True)


def get_text(submission: Submission):
    pk = submission.pk
    url = f"https://clerk.anikalegal.com/admin/questions/submission/{pk}/change/"
    return (
        f"A client has just submitted their {submission.topic} questionnaire answers for review.\n"
        f"Their submission id is <{url}|{pk}>.\n"
    )
