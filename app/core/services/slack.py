import logging

from django.conf import settings

from slack.services import send_slack_message
from core.models import Issue

logger = logging.getLogger(__name__)


def send_issue_slack(issue_pk: str):
    issue = Issue.objects.get(pk=issue_pk)
    text = get_text(issue)
    logging.info("Notifying Slack of Issue<%s>", issue_pk)
    send_slack_message(settings.SLACK_MESSAGE.CLIENT_INTAKE, text)
    # Mark request as sent
    Issue.objects.filter(pk=issue.pk).update(is_alert_sent=True)


def get_text(issue: Issue):
    pk = issue.pk
    url = f"https://clerk.anikalegal.com/admin/core/issue/{pk}/change/"
    answers = issue.answers
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

    topic = issue.topic.lower()
    return (
        f"A client has just submitted their *{topic}* questionnaire answers for review.\n"
        f"Their issue id is <{url}|{pk}>.\n"
    ) + ref_str
