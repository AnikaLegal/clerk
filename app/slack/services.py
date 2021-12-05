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

    logging.info("Sending %s", slack_msg)
    url = slack_msg.channel.webhook_url
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
    resp = requests.post(url, json=data, headers=headers)
    resp.raise_for_status()
    logger.info(f"Finished sending Slack message to user {user_id}")


def get_slack_user_by_email(email: str):
    url = "https://slack.com/api/users.lookupByEmail"
    data = {"email": email}
    resp = requests.get(url, params=data, headers=HEADERS)
    resp.raise_for_status()
    user_data = resp.json()
    logging.info(user_data)
    if user_data["ok"]:
        return user_data["user"]