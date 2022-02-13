import os
from django.core.management.base import BaseCommand
from django.conf import settings

import requests

HEADERS = {"Authorization": f"Bearer {settings.SENDGRID_API_KEY}"}
DEV_PARSE_URL = "https://api.sendgrid.com/v3/user/webhooks/parse/settings/em9463.dev-mail.anikalegal.com"


class Command(BaseCommand):
    help = "Set up inbound parse settings for dev environemnt."

    def add_arguments(self, parser):
        parser.add_argument(
            "url",
            type=str,
            help="New ngrok url to use, eg 'https://90c8-194-193-130-131.ngrok.io'",
        )

    def handle(self, *args, **kwargs):
        """
        https://app.sendgrid.com/settings/parse
        https://sendgrid.api-docs.io/v3.0/settings-inbound-parse/update-a-parse-setting
        """
        url = kwargs["url"]
        data = {
            "url": url.rstrip("/") + "/email/receive/",
            "spam_check": False,
            "send_raw": False,
        }
        resp = requests.patch(DEV_PARSE_URL, json=data, headers=HEADERS)
        resp.raise_for_status()
        print("Update success: ", resp.json())
