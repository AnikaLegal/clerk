import logging

import requests
from microsoft.endpoints.helpers import BASE_URL, HTTP_HEADERS, get_token

logger = logging.getLogger(__name__)


class MSGraphTokenError(Exception):
    """Exception raised when no token is available for MS Graph API."""

    pass


class BaseEndpoint:
    """Base class for MS Graph endpoints."""

    def __init__(self, client):
        self.client = client

    @property
    def token(self) -> str | None:
        return get_token(self.client)

    @property
    def headers(self):
        token = self.token
        if not token:
            raise MSGraphTokenError("No token available for MS Graph API")
        HTTP_HEADERS["Authorization"] = "Bearer " + token
        return HTTP_HEADERS

    def get(self, path):
        resp = requests.get(BASE_URL + path, headers=self.headers, stream=False)
        return self.handle(resp)

    def get_list(self, path) -> list:
        """Get request but follows pagination and always returns a list"""
        resp = requests.get(BASE_URL + path, headers=self.headers, stream=False)
        json = self.handle(resp)
        resp_list = []
        if json:
            resp_list += json["value"]
            next_url = json.get("@odata.nextLink", "")
            while next_url:
                resp = requests.get(next_url, headers=self.headers, stream=False)
                next_json = self.handle(resp)
                resp_list += next_json["value"]
                next_url = next_json.get("@odata.nextLink", "")

        return resp_list

    def post(self, path, data):
        resp = requests.post(
            BASE_URL + path, headers=self.headers, json=data, stream=False
        )
        return self.handle(resp)

    def patch(self, path, data):
        resp = requests.patch(
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
        except requests.exceptions.HTTPError:
            if resp.status_code == 404:
                return None
            raise

        return json
