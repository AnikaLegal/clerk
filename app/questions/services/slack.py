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

    answers = {a["name"]: a["answer"] for a in submission.answers if "name" in a}
    if "CLIENT_REFERRAL" in answers:
        ref_type = answers["CLIENT_REFERRAL"]
        ref_name = ""
        ref_name = answers.get("CLIENT_REFERRAL_CHARITY", ref_name)
        ref_name = answers.get("CLIENT_REFERRAL_LEGAL_CENTRE", ref_name)
        ref_name = answers.get("CLIENT_REFERRAL_OTHER", ref_name)
        ref_str = f"*Referral type*: {ref_type}"
        if ref_name:
            ref_str += " / " + ref_name
    else:
        ref_str = f"*Referral type*: no info available."

    topic = submission.topic.lower()
    return (
        f"A client has just submitted their *{topic}* questionnaire answers for review.\n"
        f"Their submission id is <{url}|{pk}>.\n"
    ) + ref_str
