from microsoft.base import BaseEndpoint
from microsoft.helpers import BASE_URL

from django.conf import settings

"""
from microsoft.group import GroupEndpoint
group = GroupEndpoint()
"""


class GroupEndpoint(BaseEndpoint):
    """
    Endpoint for Group (Staging or Production depending on settings)
    https://docs.microsoft.com/en-us/graph/api/resources/group
    """

    def get(self):
        """
        Get the Group.
        Returns Group object or raises HTTP error.
        """
        return super().get(f"groups/{settings.MS_GRAPH_GROUP_ID}")

    def members(self):
        """
        Lists the Group's members.
        Returns list of members or raises HTTP error.
        """
        json = super().get(f"groups/{settings.MS_GRAPH_GROUP_ID}/members")

        list_members = []

        for item in json["value"]:
            list_members.append(item["userPrincipalName"])

        return list_members

    def add_user(self, userPrincipalName):
        """
        Add User to the Group.
        Returns None or raises HTTP error.
        """
        data = {"@odata.id": f"{BASE_URL}users/{userPrincipalName}"}

        return super().post(f"groups/{settings.MS_GRAPH_GROUP_ID}/members/$ref", data)
