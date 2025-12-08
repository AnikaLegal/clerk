import logging
import os
from typing import TYPE_CHECKING
from urllib.parse import quote

import requests
from django.conf import settings

from .base import BaseEndpoint
from .helpers import BASE_URL

if TYPE_CHECKING:
    from typing import Literal, TypeAlias

    ConflictBehaviour: TypeAlias = Literal["fail", "replace", "rename"]


logger = logging.getLogger(__name__)


FILE_UPLOAD_SIZE_LIMIT = 4194304  # bytes


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
        return super().get_list(url)

    def get_all_files(self, path):
        """
        Recursively get all files inside current folder.
        """
        children = self.get_children(path)
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

    def create_folder(self, folder_name, parent_id):
        """
        Create a folder under the parent folder specified by the supplied id.
        """
        url = f"groups/{settings.MS_GRAPH_GROUP_ID}/drive/items/{parent_id}/children"
        return super().post(
            url,
            data={
                "name": folder_name,
                "folder": {},  # They do it like this in the docs /shrug
                "@microsoft.graph.conflictBehavior": "fail",
            },
        )

    def create_path(self, path):
        """
        Create a folder path under the root folder.
        """
        parent_id = "root"
        partial_path = ""
        for part in path.split(os.path.sep):
            partial_path = os.path.join(partial_path, part)
            info = self.get(partial_path)
            if not info:
                self.create_folder(part, parent_id)
                info = self.get(partial_path)
            parent_id = info["id"]

    def upload_file(
        self,
        file,
        parent_id,
        name=None,
        conflict_behaviour: "ConflictBehaviour" = "fail",
    ):
        """
        Uploads file to parent
        """
        name = name or file.name
        if file.size < FILE_UPLOAD_SIZE_LIMIT:
            data = self._upload_small_file(file, parent_id, name, conflict_behaviour)
        else:
            data = self._upload_large_file(file, parent_id, name, conflict_behaviour)
        return data

    def get_child_if_exists(self, filename, parent_id):
        # Check for existing file.
        url = f"/groups/{settings.MS_GRAPH_GROUP_ID}/drive/items/{parent_id}/children"
        children = super().get_list(url)
        for f in children:
            if filename == f["name"]:
                return f

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
        url = os.path.join(self.MIDDLE_URL, f"{quote(path)}:/copy")

        return super().post(url, data)

    def list_permissions(self, path):
        """
        List the Folder's permissions.
        Returns list of permissions or None if Folder doesn't exist.
        """
        url = os.path.join(self.MIDDLE_URL, f"{path}:/permissions")
        perms = super().get_list(url)
        if perms:
            list_permissions = []
            for item in perms:
                try:
                    list_permissions.append((item["id"], item["grantedToV2"]))
                except Exception:
                    logger.exception("Malformed Sharepoint permission")
            return list_permissions

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

    def _upload_small_file(
        self,
        file,
        parent_id,
        filename,
        conflict_behaviour: "ConflictBehaviour",
    ):
        url = os.path.join(
            BASE_URL,
            f"groups/{settings.MS_GRAPH_GROUP_ID}/drive/items/{parent_id}:/{quote(filename)}:/content",
        )
        params = {
            "@microsoft.graph.conflictBehavior": conflict_behaviour,
        }

        headers = {**self.headers}
        content_type = getattr(file, "content_type", "")
        if content_type:
            headers["Content-Type"] = content_type
        resp = requests.put(url, params=params, data=file, headers=headers, stream=True)
        return self.handle(resp)

    def _upload_large_file(
        self,
        file,
        parent_id,
        filename,
        conflict_behaviour: "ConflictBehaviour",
    ):
        # Start an upload session
        url = os.path.join(
            BASE_URL,
            f"groups/{settings.MS_GRAPH_GROUP_ID}/drive/items/{parent_id}:/{quote(filename)}:/createUploadSession",
        )
        params = {
            "@microsoft.graph.conflictBehavior": conflict_behaviour,
        }

        data = {"name": filename}
        resp = requests.post(
            url, params=params, json=data, headers=self.headers, stream=False
        )

        session_data = self.handle(resp)
        upload_url = session_data["uploadUrl"]

        CHUNK_SIZE = 10485760
        chunks = int(file.size / CHUNK_SIZE) + 1 if file.size % CHUNK_SIZE > 0 else 0
        start = 0
        file.seek(0)
        for _ in range(chunks):
            chunk = file.read(CHUNK_SIZE)
            bytes_read = len(chunk)
            upload_range = f"bytes {start}-{start + bytes_read - 1}/{file.size}"
            resp = requests.put(
                upload_url,
                headers={
                    "Content-Length": str(bytes_read),
                    "Content-Range": upload_range,
                    **self.headers,
                },
                data=chunk,
            )
            resp.raise_for_status()
            start += bytes_read

        return self.get_child_if_exists(filename, parent_id)
