import logging
from urllib.parse import urljoin

import requests

from .base import BaseEndpoint

logger = logging.getLogger(__file__)


class ActionEndpoint(BaseEndpoint):
    """
    Endpoint for Actionstep actions.
    https://actionstep.atlassian.net/wiki/spaces/API/pages/12025956/Actions
    """

    resource = "actions"

    def __init__(self, *args, **kwargs):
        self.action_create = ActionCreateEndpoint(*args, **kwargs)
        self.action_types = ActionTypesEndpoint(*args, **kwargs)
        super().__init__(*args, **kwargs)

    def get_next_ref(self, prefix: str):
        """
        Returns next file reference.
        Eg. prefix of "R" would get "R0001"
        """
        actions = self.list({"reference_ilike": f"{prefix}*"})
        max_ref_num = 0
        for action in actions:
            try:
                ref_num = int(action["reference"].replace(prefix, ""))
            except Exception:
                logger.exception(
                    "Error parsing matter reference %s", action["reference"]
                )
                ref_num = 0

            if ref_num > max_ref_num:
                max_ref_num = ref_num

        next_ref = max_ref_num + 1
        return prefix + str(next_ref).rjust(4, "0")

    def get(self, action_id: str):
        params = {"id": action_id}
        resp_data = super().get(params)
        return resp_data[self.resource]

    def list(self, params=None):
        resp_data = super().get(params)
        data = resp_data[self.resource] if resp_data else None
        return self._ensure_list(data)

    def update(self, action_id: str, data: dict):
        data = {self.resource: [data]}
        return super().update(filenote_id, data)

    def create(self, *args, **kwargs):
        """
        Create an action - this is a separate API.
        """
        return self.action_create.create(*args, **kwargs)


class ActionTypesEndpoint(BaseEndpoint):
    """
    Endpoint for action tpes.
    https://actionstep.atlassian.net/wiki/spaces/API/pages/21135476/Action+Types
    """

    resource = "actiontypes"

    def get_for_name(self, name: str):
        params = {"name": name}
        resp_data = super().get(params)
        return resp_data[self.resource]

    def list(self):
        resp_data = super().get()
        data = resp_data[self.resource]
        return self._ensure_list(data)


class ActionCreateEndpoint(BaseEndpoint):
    """
    Endpoint for creating actions.
    https://actionstep.atlassian.net/wiki/spaces/API/pages/40108259/Action+Create
    """

    resource = "actioncreate"

    def create(
        self,
        submission_id: str,
        action_type_id: int,
        action_name: str,
        file_reference: str,
        participant_id: str,
    ):
        """
        Create an action - this is a separate API.
        """
        data = {
            "actioncreate": {
                "actionName": action_name,
                "fileReference": file_reference,
                "fileNote": f"Created automatically by Anika Clerk for submission {submission_id}",
                "links": {
                    "actionType": str(action_type_id),
                    "assignedToParticipant": str(participant_id),
                },
            }
        }
        resp_data = super().create(data)
        return resp_data[self.resource]
