import msal
import logging
import requests
import random
import string
from .helpers import BASE_URL, create_client, get_token
from django.conf import settings


logger = logging.getLogger(__name__)


class MSGraphAPI:
    def __init__(self):
        self.client = create_client(
            settings.AZURE_AD_CLIENT_ID,
            settings.MS_AUTHORITY_URL,
            settings.AZURE_AD_CLIENT_SECRET,
        )
        self.access_token = get_token(self.client)
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.access_token,
        }

    def user_exists(self, email: str) -> bool:
        endpoint = BASE_URL + "users/" + email
        response = requests.get(endpoint, headers=self.headers, stream=False)
        return response.status_code < 300

    def create_user(self, email, first_name, last_name) -> str:
        endpoint = BASE_URL + "users"
        password = generate_password(16)
        data = {
            "accountEnabled": True,
            "displayName": f"{first_name} {last_name}",
            "mailNickname": first_name,
            "userPrincipalName": email,
            "usageLocation": "AU",
            "passwordProfile": {
                "forceChangePasswordNextSignIn": True,
                "password": password,
            },
        }
        return requests.post(endpoint, headers=self.headers, json=data, stream=False)


def generate_password(length):
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


"""
from microsoft.wrapper import MSGraphAPI
api = MSGraphAPI()
"""
