import requests
import logging
from pprint import pformat

from microsoft.helpers import create_client, get_token, BASE_URL, HTTP_HEADERS

from django.conf import settings


logger = logging.getLogger(__name__)


class MSGraph:
    """This class allows us to make basic API calls to MS Graph."""

    def __init__(self):
        # Authenticate and obtain access token.
        client = create_client(
            settings.AZURE_AD_CLIENT_ID,
            settings.MS_AUTHORITY_URL,
            settings.AZURE_AD_CLIENT_SECRET,
        )
        access_token = get_token(client)

        # Set HTTP headers for making API calls.
        HTTP_HEADERS["Authorization"] = "Bearer " + access_token
        self.headers = HTTP_HEADERS

    def get(self, path):
        resp = requests.get(BASE_URL + path, headers=self.headers, stream=False)
        return self.handle(resp)

    def post(self, path, data):
        resp = requests.post(
            BASE_URL + path, headers=self.headers, json=data, stream=False
        )
        return self.handle(resp)

    def delete(self, path):
        resp = requests.delete(BASE_URL + path, headers=self.headers, stream=False)
        return self.handle(resp)

    def handle(self, resp):
        # Collect response body as JSON.
        json = resp.json() if resp.content else None

        # Deal with unsuccessful requests.
        try:
            resp.raise_for_status()
        except requests.HTTPError:
            pretty_json = pformat(json, indent=2)
            req = resp.request
            logger.error(
                f"{req.method} {req.url} failed with response body: {pretty_json}"
            )
            raise

        return json


"""
from microsoft.wrapper import MSGraph
api = MSGraph()
"""
