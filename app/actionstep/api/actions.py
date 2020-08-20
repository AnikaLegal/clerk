import logging
from urllib.parse import urljoin

import requests

from .base import BaseEndpoint

logger = logging.getLogger(__file__)


class ActionEndpoint(BaseEndpoint):
    """
    Endpoint for Actionstep actions.
    https://actionstep.atlassian.net/wiki/spaces/API/pages/12025956/Actions
    Example action schema:
    {
        'id': 65,
        'name': 'Fakey McFakeFake',
        'reference': 'R0123',
        'priority': 0,
        'status': 'Closed',
        'statusTimestamp': '2020-07-09T19:34:10+12:00',
        'isBillableOverride': None,
        'createdTimestamp': '2020-07-02',
        'modifiedTimestamp': '2020-07-11T07:30:51+12:00',
        'isDeleted': 'F',
        'deletedBy': None,
        'deletedTimestamp': None,
        'isFavorite': 'F',
        'overrideBillingStatus': None,
        'lastAccessTimestamp': '2020-07-30T16:41:33+12:00',
        'links': {'assignedTo': '11',
        'actionType': '28',
        'primaryParticipants': ['159'],
        'relatedActions': None}
    }
    """

    resource = "actions"

    def __init__(self, *args, **kwargs):
        self.action_create = ActionCreateEndpoint(*args, **kwargs)
        self.action_types = ActionTypesEndpoint(*args, **kwargs)
        super().__init__(*args, **kwargs)

    def get_next_ref(self, prefix: str):
        """
        Returns next file reference string.
        Eg. prefix of "R" would return "R0001"
        """
        actions = self.list({"reference_ilike": f"{prefix}*"})
        max_ref_num = 0
        for action in actions:
            try:
                ref_num = int(action["reference"].replace(prefix, ""))
            except Exception:
                logger.exception("Error parsing matter reference %s", action["reference"])
                ref_num = 0

            if ref_num > max_ref_num:
                max_ref_num = ref_num

        next_ref = max_ref_num + 1
        return prefix + str(next_ref).rjust(4, "0")

    def get(self, action_id: str):
        """
        Gets an action.
        Returns action (see schema above) or None.
        """
        return super().get({"id": action_id})

    def create(self, *args, **kwargs):
        """
        Create an action.
        Returns action (see schema above).
        """
        return self.action_create.create(*args, **kwargs)


class ActionTypesEndpoint(BaseEndpoint):
    """
    Endpoint for action tpes.
    https://actionstep.atlassian.net/wiki/spaces/API/pages/21135476/Action+Types
    """

    resource = "actiontypes"

    def get_for_name(self, name: str):
        return super().get({"name": name})


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
        timestamp: str = ""
    ):
        """
        Create an action - this is a separate API.
        """
        data = {
            "actionName": action_name,
            "fileReference": file_reference,
            "fileNote": f"Created automatically by Anika Clerk for submission {submission_id}",
            "links": {
                "actionType": str(action_type_id),
                "assignedToParticipant": str(participant_id),
            },
        }
        if timestamp:
            data["timestamp"] = timestamp
        return super().create(data)
