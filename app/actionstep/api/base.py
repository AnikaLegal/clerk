import logging
from json.decoder import JSONDecodeError
from urllib.parse import urljoin

import requests

logger = logging.getLogger(__file__)


class BaseEndpoint:
    """
    Base class for Actionstep endpoints.

    FIXME: Handle expired token race condition
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

    def get(self, params=None) -> dict:
        """
        Gets a resource, filtered by params.
        Returns a dict or None.
        """
        objs = self.list(params)
        if not objs:
            # Empty list.
            return None
        else:
            # Non-empty list.
            assert len(objs) == 1, f"Wrong number of objs for get: {objs}"
            return objs[0]

    def list(self, params=None) -> list:
        """
        Get a resource, filtered by params.
        Returns a list of results.
        """
        return self._list(self.url, params)

    def _list(self, url, params=None) -> list:
        resp = requests.get(url, params=params, headers=self.headers)
        response_data = self._handle_json_response(url, resp)
        if not response_data:
            # Nothing found.
            return []

        data = response_data[self.resource]
        results = []
        results += data if type(data) is list else [data]
        try:
            paging = response_data["meta"]["paging"][self.resource]
        except (TypeError, KeyError):
            paging = None

        if paging and paging["nextPage"]:
            results += self._list(paging["nextPage"])

        return results

    def create(self, data: dict):
        """
        Create a resource with provided data.
        Returns the created object.
        """
        url = self.url
        request_data = {self.resource: [data]}
        resp = requests.post(url, json=request_data, headers=self.headers)
        response_data = self._handle_json_response(url, resp)
        return response_data[self.resource]

    def update(self, resource_id: str, data: dict):
        """
        Update data in an existing resource.
        Returns the created object.
        """
        url = urljoin(self.url, str(resource_id))
        request_data = {self.resource: [data]}
        resp = requests.put(url, json=data, headers=self.headers)
        response_data = self._handle_json_response(url, resp)
        return response_data[self.resource]

    def delete(self, resource_id: str):
        """
        Delete an existing resource,
        May result in a soft-delete.
        Returns None
        """
        url = urljoin(self.url, str(resource_id))
        resp = requests.delete(url, headers=self.headers)
        self._handle_json_response(url, resp)

    def _handle_json_response(self, url, resp):
        json = self._try_json_decode(resp)
        try:
            resp.raise_for_status()
        except requests.HTTPError:
            logger.exception("Actionstep API called failed: %s", json)
            raise

        return json

    def _try_json_decode(self, resp):
        if resp.status_code == 204:
            # No content
            return None
        else:
            return resp.json()
