import logging

import requests
from django.conf import settings

from .models import SlackMessage


def send_slack_message(message_slug: str, message_text: str):
    """
    Send a Slack message to a given user
    """
    slack_msg = (
        SlackMessage.objects.select_related("channel")
        .prefetch_related("users")
        .get(slug=message_slug)
    )
    users = list(slack_msg.users.all())
    if users:
        user_text = " and ".join([f"<@{u.slack_id}>" for u in users])
        user_greeting_text = f"Hi {user_text}."
        text = "\n\n".join([user_greeting_text, message_text, ":heart: Client Bot :robot_face:"])
    else:
        text = message_text

    logging.info("Sending %s", slack_msg)
    url = slack_msg.channel.webhook_url
    resp = requests.post(url, json={"text": text}, headers={"Content-Type": "application/json"})
    resp.raise_for_status()
