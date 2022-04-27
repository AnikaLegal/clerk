import logging
import requests

from microsoft.endpoints.helpers import BASE_URL, HTTP_HEADERS

logger = logging.getLogger(__name__)


class BaseEndpoint:
    """Base class for MS Graph endpoints."""

    def __init__(self, access_token):
        HTTP_HEADERS["Authorization"] = "Bearer " + access_token
        self.headers = HTTP_HEADERS

    def get(self, path):
        resp = requests.get(BASE_URL + path, headers=self.headers, stream=False)
        json = self.handle(resp)
        if json:
            next_url = json.get("@odata.nextLink", "")
            while next_url:
                resp = requests.get(next_url, headers=self.headers, stream=False)
                next_json = self.handle(resp)
                json["values"] += next_json["values"]
                next_url = next_json.get("@odata.nextLink", "")

        return json

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
            else:
                logger.error(
                    f"{resp.request.method} {resp.request.url} failed with response body: {json}"
                )
                raise

        return json
