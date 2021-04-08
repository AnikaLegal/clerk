import logging

from django.conf import settings

from core.models import Issue
from slack.services import send_slack_message

logger = logging.getLogger(__name__)


def send_issue_slack(issue_pk: str):
    issue = Issue.objects.select_related("client").get(pk=issue_pk)
    text = get_text(issue)
    logging.info("Notifying Slack of Issue<%s>", issue_pk)
    send_slack_message(settings.SLACK_MESSAGE.CLIENT_INTAKE, text)
    # Mark request as sent
    Issue.objects.filter(pk=issue.pk).update(is_alert_sent=True)


def get_text(issue: Issue):
    pk = issue.pk
    url = f"https://clerk.anikalegal.com/admin/core/issue/{pk}/change/"

    referrer_type = issue.client.referrer_type.title().replace("_", " ")
    referrer = issue.client.referrer

    if referrer_type:
        ref_str = f"*Referral type*: {referrer_type}"
        if referrer:
            ref_str += f" / {referrer}"
    else:
        ref_str = f"*Referral type*: no info available."

    topic = issue.topic.lower()
    return (
        f"A client has just submitted their *{topic}* questionnaire answers for review.\n"
        f"Their issue id is <{url}|{pk}>.\n"
    ) + ref_str
