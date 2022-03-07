import os
import logging

import requests
from django.conf import settings
from django.utils.text import slugify

from .base import BaseEndpoint
from .helpers import BASE_URL


logger = logging.getLogger(__name__)


class FolderEndpoint(BaseEndpoint):
    """
    Endpoint for Folder.
    https://docs.microsoft.com/en-us/graph/api/resources/driveitem
    """

    MIDDLE_URL = f"groups/{settings.MS_GRAPH_GROUP_ID}/drive/root:/"

    def get(self, path):
        """
        Get the Folder inside the Group Drive (filesystem).
        Returns driveItem object or None.
        """
        url = os.path.join(self.MIDDLE_URL, path)

        return super().get(url)

    def get_children(self, path):
        """
        Get child items (folders, files) inside current folder
        """
        url = os.path.join(self.MIDDLE_URL, f"{path}:/children")

        return super().get(url)

    def get_all_files(self, path):
        """
        Recursively get all files inside current folder.
        """
        children_data = self.get_children(path)
        children = children_data["value"] if children_data else []

        all_files = []

        for item in children:
            if item.get("file"):
                all_files.append(item)
            elif item.get("folder"):
                has_children = item.get("folder", {}).get("childCount", 0) > 0

                if has_children:
                    folder_children = self.get_all_files(
                        os.path.join(path, item["name"])
                    )
                    all_files += folder_children

        return all_files

    def upload_file(self, file, parent_id):
        """
        Uploads file to parent
        """
        original_filename = file.name
        filename, ext = os.path.splitext(original_filename)
        filename = slugify(filename) + ext
        url = os.path.join(
            BASE_URL,
            f"groups/{settings.MS_GRAPH_GROUP_ID}/drive/items/{parent_id}:/{filename}:/content",
        )
        headers = {**self.headers}
        headers["Content-Type"] = file.content_type
        resp = requests.put(url, data=file, headers=headers, stream=True)
        data = self.handle(resp)
        # Rename file
        file_id = data["id"]
        url = f"groups/{settings.MS_GRAPH_GROUP_ID}/drive/items/{file_id}"
        return super().patch(url, data={"name": original_filename})

    def delete_file(self, file_id):
        url = f"groups/{settings.MS_GRAPH_GROUP_ID}/drive/items/{file_id}"
        return super().delete(url)

    def download_file(self, file_id):
        """
        Returns file name, MIME type, file bytes
        """
        file_data = super().get(
            f"groups/{settings.MS_GRAPH_GROUP_ID}/drive/items/{file_id}"
        )
        file_name = file_data["name"]
        mimetype = file_data["file"]["mimeType"]

        url = os.path.join(
            BASE_URL,
            f"groups/{settings.MS_GRAPH_GROUP_ID}/drive/items/{file_id}/content",
        )
        resp = requests.get(url, headers=self.headers, stream=False)
        resp.raise_for_status()

        return file_name, mimetype, resp.content

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
        url = os.path.join(self.MIDDLE_URL, f"{path}:/copy")

        return super().post(url, data)

    def list_permissions(self, path):
        """
        List the Folder's permissions.
        Returns list of permissions or None if Folder doesn't exist.
        """
        url = os.path.join(self.MIDDLE_URL, f"{path}:/permissions")

        json = super().get(url)

        if json:
            list_permissions = []

            for item in json["value"]:
                try:
                    list_permissions.append((item["id"], item["grantedTo"]))
                except Exception:
                    logger.exception("Malformed Sharepoint permission")

            return list_permissions
        else:
            return None

    def delete_permission(self, path, perm_id):
        """
        Delete specific permission for a Folder.
        Returns None if successful or Folder doesn't exist.
        Raises HTTPError if permission doesn't exist.
        """
        url = os.path.join(self.MIDDLE_URL, f"{path}:/permissions/{perm_id}")

        return super().delete(url)

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
        url = os.path.join(self.MIDDLE_URL, f"{path}:/invite")

        return super().post(url, data)
