from django.core.management.base import BaseCommand

from emails.api import set_inbound_parse_url


class Command(BaseCommand):
    help = "Set up inbound parse settings for dev environemnt."

    def add_arguments(self, parser):
        parser.add_argument(
            "url",
            type=str,
            help="New ngrok url to use, eg 'https://90c8-194-193-130-131.ngrok.io'",
        )

    def handle(self, *args, **kwargs):
        url = kwargs["url"]
        resp_data = set_inbound_parse_url(url)
        print("Update success: ", resp_data)
