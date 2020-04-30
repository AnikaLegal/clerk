import logging

import requests
from django.conf import settings

from webhooks.models import WebflowContact

logger = logging.getLogger(__name__)


def send_webflow_contact_slack(webflow_contact_pk: str):
    url = settings.SUBMIT_SLACK_WEBHOOK_URL
    webflow_contact = WebflowContact.objects.get(pk=webflow_contact_pk)
    text = get_text(webflow_contact)
    logging.info("Notifying Slack of WebflowContact<%s>", webflow_contact_pk)
    resp = requests.post(url, json={"text": text}, headers={"Content-Type": "application/json"})
    resp.raise_for_status()
    # Mark request as sent
    WebflowContact.objects.filter(pk=webflow_contact.pk).update(is_alert_sent=True)


def get_text(webflow_contact: WebflowContact):
    return f"""Hi <@{settings.SLACK_USER.SAM}>.

A client has just submitted a contact form on the landing page.
Check out ID #{webflow_contact.pk} at https://clerk.anikalegal.com/admin/webhooks/webflowcontact/

:heart: Client Bot :robot_face:
"""
