import logging

from django.conf import settings

from slack.services import send_slack_message
from webhooks.models import WebflowContact

logger = logging.getLogger(__name__)


def send_webflow_contact_slack(webflow_contact_pk: str):
    webflow_contact = WebflowContact.objects.get(pk=webflow_contact_pk)
    text = get_text(webflow_contact)
    logger.info("Notifying Slack of WebflowContact<%s>", webflow_contact_pk)
    send_slack_message(settings.SLACK_MESSAGE.LANDING_FORM, text)
    # Mark request as sent
    WebflowContact.objects.filter(pk=webflow_contact.pk).update(is_alert_sent=True)


def get_text(webflow_contact: WebflowContact):
    pk = str(webflow_contact.pk)
    url = settings.CLERK_BASE_URL + "/admin/webhooks/webflowcontact/" + pk
    return (
        "A contact request has been submitted via the landing page contact form.\n"
        f"You can view the request here: <{url}|{pk}>.\n"
    )
