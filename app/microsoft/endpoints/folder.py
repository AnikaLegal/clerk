import os

import requests
from django.conf import settings

from .base import BaseEndpoint
from .helpers import BASE_URL


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

    def get_children(self, path):
        """
        Get the child items inside a folder.
        """
        url = os.path.join(self.base_url, f"root:/{path}:/children")
        data = super().get(url)
        return data

    def get_all_files(self, path):
        """
        Get all files inside a folder.
        """
        url = os.path.join(self.base_url, f"root:/{path}:/children")
        children_data = super().get(url)
        files = []
        children = children_data["value"] if children_data else []
        for item in children:
            if item.get("file"):
                # It's a file
                files.append(item)
            elif item.get("folder"):
                # It's a folder
                has_children = item.get("folder", {}).get("childCount", 0) > 0
                if has_children:
                    folder_path = os.path.join(path, item["name"])
                    folder_child_files = self.get_all_files(folder_path)
                    files += folder_child_files

        return files

    def download_file(self, file_drive_id):
        """
        Returns filename, minemtype, file bytes
        """
        file_url = os.path.join(self.base_url, f"items/{file_drive_id}")
        file_data = super().get(file_url)
        filename = file_data["name"]
        mimetype = file_data["file"]["mimeType"]
        url = os.path.join(BASE_URL, self.base_url, f"items/{file_drive_id}/content")
        resp = requests.get(url, headers=self.headers, stream=False)
        resp.raise_for_status()
        return filename, mimetype, resp.content

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
