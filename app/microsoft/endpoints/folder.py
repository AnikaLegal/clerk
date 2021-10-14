import os
from django.conf import settings

from .base import BaseEndpoint


class FolderEndpoint(BaseEndpoint):
    """
    Endpoint for Folder.
    https://docs.microsoft.com/en-us/graph/api/resources/driveitem
    """

    base_url = f"groups/{settings.MS_GRAPH_GROUP_ID}/drive"

    def get(self, path):
        """
        Get the Folder inside the Group (Staging or Production) Drive (filesystem).
        Returns driveItem object or None.
        """
        url = os.path.join(self.base_url, f"root:/{path}")
        return super().get(url)

    def files(self, path):
        """
        Get the Files inside a Folder.
        Returns list of Files or None if Folder doesn't exist.
        """
        url = os.path.join(self.base_url, f"root:/{path}:/children")
        data = super().get(url)
        if data:
            list_files = []
            for item in data["value"]:
                file = item["name"], item["webUrl"]
                list_files.append(file)

            return list_files

    def copy(self, path, name, parent_id):
        """
        Make copy of an existing Folder.
        Returns None if successful or if Folder doesn't exist.
        Raises HTTPError if copy name already exists.
        """
        # We have the option of specifying the name of the copy and its parent Folder.
        data = {
            "name": name,
            "parentReference": {"driveId": settings.MS_GRAPH_DRIVE_ID, "id": parent_id},
        }
        url = os.path.join(self.base_url, f"root:/{path}:/copy")
        return super().post(url, data)

    def list_permissions(self, path):
        """
        List the Folder's permissions.
        Returns list of permissions or None if Folder doesn't exist.
        """
        url = os.path.join(self.base_url, f"root:/{path}:/permissions")
        return super().get(url)

    def delete_permission(self, path, perm_id):
        """
        Delete specific permission for a Folder.
        Returns None if successful or Folder doesn't exist.
        Raises HTTPError if permission doesn't exist.
        """
        return super().delete(
            f"groups/{settings.MS_GRAPH_GROUP_ID}/drive/root:/{path}:/permissions/{perm_id}"
        )

    def create_permissions(self, path, role, emails):
        """
        Create permissions (read or write) for a Folder.
        Returns permissions created or None if Folder doesn't exist.
        """
        assert role in ["read", "write"]
        data = {
            # Do not remove fields or POST request might fail.
            "requireSignIn": True,
            "sendInvitation": False,
            "roles": [role],
            "recipients": [{"email": email} for email in emails],
        }

        return super().post(
            f"groups/{settings.MS_GRAPH_GROUP_ID}/drive/root:/{path}:/invite", data
        )
