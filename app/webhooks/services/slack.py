import logging

from django.conf import settings

from slack.services import send_slack_message
from webhooks.models import WebflowContact

logger = logging.getLogger(__name__)


def send_webflow_contact_slack(webflow_contact_pk: str):
    webflow_contact = WebflowContact.objects.get(pk=webflow_contact_pk)
    text = get_text(webflow_contact)
    logging.info("Notifying Slack of WebflowContact<%s>", webflow_contact_pk)
    send_slack_message(settings.SLACK_MESSAGE.LANDING_FORM, text)
    # Mark request as sent
    WebflowContact.objects.filter(pk=webflow_contact.pk).update(is_alert_sent=True)


def get_text(webflow_contact: WebflowContact):
    return (
        "A client has just submitted a contact form on the landing page.\n"
        f"Check out ID #{webflow_contact.pk} at "
        "https://www.anikalegal.com/admin/webhooks/webflowcontact/"
    )
