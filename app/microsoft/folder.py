from microsoft.base import BaseEndpoint

from django.conf import settings


class FolderEndpoint(BaseEndpoint):
    """
    Endpoint for Folder.
    https://docs.microsoft.com/en-us/graph/api/resources/driveitem
    """

    def get(self, path):
        """
        Get the Folder inside the Group (Staging or Production) Drive (filesystem).
        Returns driveItem object or None.
        """
        return super().get(f"groups/{settings.MS_GRAPH_GROUP_ID}/drive/root:/{path}")

    def files(self, path):
        """
        Get the Files inside a Folder.
        Returns list of Files or None if Folder doesn't exist.
        """
        json = super().get(
            f"groups/{settings.MS_GRAPH_GROUP_ID}/drive/root:/{path}:/children"
        )

        if json:
            list_files = []

            for item in json["value"]:
                file = item["name"], item["webUrl"]
                list_files.append(file)

            return list_files
        else:
            return None

    def copy(self, path, name):
        """
        Make copy of an existing Folder.
        Returns None if successful or if Folder doesn't exist.
        Raises HTTPError if copy name already exists
        """
        # We have the option of specifying the name of the copy and its parent Folder.
        data = {"name": name}

        return super().post(
            f"groups/{settings.MS_GRAPH_GROUP_ID}/drive/root:/{path}:/copy", data
        )

    def list_permissions(self, path):
        """
        List the Folder's permissions.
        Returns list of permissions or None if Folder doesn't exist.
        """
        json = super().get(
            f"groups/{settings.MS_GRAPH_GROUP_ID}/drive/root:/{path}:/permissions"
        )

        if json:
            list_permissions = []

            for item in json["value"]:
                list_permissions.append(item["id"])

            return list_permissions
        else:
            return None

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
