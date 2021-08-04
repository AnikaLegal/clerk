import requests

from microsoft.helpers import create_client, get_token, BASE_URL, HTTP_HEADERS

from django.conf import settings


class MSGraph:
    """This class manages authentication, basic API calls, and exceptions handling for MS Graph"""

    def __init__(self):
        # Authenticate and obtain access token.
        client = create_client(
            settings.AZURE_AD_CLIENT_ID,
            settings.MS_AUTHORITY_URL,
            settings.AZURE_AD_CLIENT_SECRET,
        )
        access_token = get_token(client)

        # Set HTTP Headers for making API calls.
        HTTP_HEADERS["Authorization"] = "Bearer " + access_token
        self.headers = HTTP_HEADERS


"""
from microsoft.wrapper import MSGraph
api = MSGraph()
"""
