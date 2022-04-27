from .base import BaseEndpoint
from .helpers import BASE_URL

from django.conf import settings


class GroupEndpoint(BaseEndpoint):
    """
    Endpoint for Group (Staging or Production depending on settings).
    https://docs.microsoft.com/en-us/graph/api/resources/group
    """

    def get(self):
        """
        Get the Group.
        Returns Group object or None.
        """
        return super().get(f"groups/{settings.MS_GRAPH_GROUP_ID}")

    def get_drive(self):
        """
        Return group drive information.
        """
        return super().get(f"groups/{settings.MS_GRAPH_GROUP_ID}/drive")

    def members(self):
        """
        List Group members.
        Returns list of members or empty list.
        """
        members = super().get_list(f"groups/{settings.MS_GRAPH_GROUP_ID}/members")
        return [item["userPrincipalName"] for item in members]

    def add_user(self, userPrincipalName):
        """
        Add User to the Group.
        Returns None if successful or raises HTTPError if User already in Group.
        """
        data = {"@odata.id": f"{BASE_URL}users/{userPrincipalName}"}

        return super().post(f"groups/{settings.MS_GRAPH_GROUP_ID}/members/$ref", data)

    def remove_user(self, userId):
        """
        Remove User from Group.
        Returns None if successful or if User isn't in the Group.
        """
        return super().delete(
            f"groups/{settings.MS_GRAPH_GROUP_ID}/members/{userId}/$ref"
        )
