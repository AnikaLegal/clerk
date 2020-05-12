import logging
from urllib.parse import urljoin
from json.decoder import JSONDecodeError

import requests

logger = logging.getLogger(__file__)


class BaseEndpoint:
    """
    Base class for Actionstep endpoints.

    TODO: Pagination support.
    """

    resource = None

    def __init__(self, base_url: str, access_token: str):
        self.rest_url = urljoin(base_url, "rest") + "/"
        self.url = urljoin(self.rest_url, self.resource) + "/"
        self.headers = {
            "Content-Type": "application/vnd.api+json",
            "Accept": "application/vnd.api+json",
            "Authorization": f"Bearer {access_token}",
        }

    def get(self, params=None):
        """
        Get a resource, filtered by params.
        Return value may be None if object has been deleted.
        """
        url = self.url
        resp = requests.get(url, params=params, headers=self.headers)
        return self._handle_json_response(url, resp)

    def create(self, data: dict):
        """
        Create a resource with provided data.
        """
        url = self.url
        resp = requests.post(url, json=data, headers=self.headers)
        return self._handle_json_response(url, resp)

    def update(self, resource_id: str, data: dict):
        """
        Update data in an existing resource.
        """
        url = urljoin(self.url, str(resource_id))
        resp = requests.put(url, json=data, headers=self.headers)
        return self._handle_json_response(url, resp)

    def delete(self, resource_id: str):
        """
        Delete an existing resource,
        May result in a soft-delete.
        """
        url = urljoin(self.url, str(resource_id))
        resp = requests.delete(url, headers=self.headers)
        return self._handle_json_response(url, resp)

    def _handle_json_response(self, url, resp):
        json = self._try_json_decode(resp)
        try:
            resp.raise_for_status()
        except requests.HTTPError:
            logger.exception("Actionstep API called failed: %s", json)
            raise

        return json

    def _try_json_decode(self, resp):
        try:
            return resp.json()
        except JSONDecodeError:
            return None

    def _ensure_list(self, data):
        """
        Actionstep sometimes returns a list or dict depending on the data.
        Returns a list if it's not already a list.
        """
        if type(data) is list:
            return data
        elif data:
            return [data]
        else:
            return []
