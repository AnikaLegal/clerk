import logging

import requests
from django.conf import settings

from .models import SlackMessage

HEADERS = {"Authorization": f"Bearer {settings.SLACK_API_TOKEN}"}

logger = logging.getLogger(__name__)


def send_slack_message(message_slug: str, message_text: str):
    """
    Send a Slack message to a given user
    """
    logger.info(f"Sending Slack message of type {message_slug}")
    slack_msg = (
        SlackMessage.objects.select_related("channel")
        .prefetch_related("users")
        .get(slug=message_slug)
    )
    users = list(slack_msg.users.all())
    if users:
        user_text = " and ".join([f"<@{u.slack_id}>" for u in users])
        user_greeting_text = f"Hi {user_text}."
        text = "\n\n".join(
            [user_greeting_text, message_text, ":heart: Client Bot :robot_face:"]
        )
    else:
        text = message_text

    logger.info("Sending %s", slack_msg)
    url = slack_msg.channel.webhook_url
    if not settings.SLACK_MESSAGE_DISABLED:
        resp = requests.post(
            url, json={"text": text}, headers={"Content-Type": "application/json"}
        )
        resp.raise_for_status()
    logger.info(f"Finished sending Slack message of type {message_slug}")


def send_slack_direct_message(markdown_text: str, user_id: str):
    logger.info(f"Sending Slack message to user {user_id}")
    headers = {"Content-Type": "application/json", **HEADERS}
    url = "https://slack.com/api/chat.postMessage"
    data = {"channel": user_id, "text": markdown_text}
    if not settings.SLACK_MESSAGE_DISABLED:
        resp = requests.post(url, json=data, headers=headers)
        resp.raise_for_status()
    logger.info(f"Finished sending Slack message to user {user_id}")


# Slack accounts can lag behind Clerk while the User Domain Migration is in
# progress. Remove this fallback once everyone has confirmed the change in Slack.
OLD_EMAIL_DOMAIN = "@anikalegal.com"
NEW_EMAIL_DOMAIN = "@anikalegal.org.au"


def get_slack_user_by_email(email: str):
    slack_user = _lookup_slack_user(email)
    if not slack_user and email.endswith(NEW_EMAIL_DOMAIN):
        old_email = email.removesuffix(NEW_EMAIL_DOMAIN) + OLD_EMAIL_DOMAIN
        slack_user = _lookup_slack_user(old_email)
        if slack_user:
            logger.info(f"Found Slack user for {email} via {old_email}")
    return slack_user


def _lookup_slack_user(email: str):
    url = "https://slack.com/api/users.lookupByEmail"
    data = {"email": email}
    resp = requests.get(url, params=data, headers=HEADERS)
    if not settings.SLACK_MESSAGE_DISABLED:
        resp.raise_for_status()
        user_data = resp.json()
        logger.info(user_data)
        if user_data["ok"]:
            return user_data["user"]
