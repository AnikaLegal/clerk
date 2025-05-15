import os
from django.core.files.storage import Storage
from microsoft.endpoints import MSGraphAPI
from urllib.parse import quote


class MSGraphStorage(Storage):
    def __init__(self, base_path):
        self.api = MSGraphAPI()
        self.base_path = base_path

    def _get_full_path(self, name):
        path = os.path.join(self.base_path, name)
        head, tail = os.path.split(path)
        return os.path.join(head, quote(tail))

    def _get_file_info(self, name, select=None):
        full_path = self._get_full_path(name)
        return self.api.folder.get(full_path, select)

    def _open(self, name, mode="rb"):
        # Retrieve the file from Microsoft Graph
        file_info = self._get_file_info(name, select=["id"])
        if not file_info:
            raise FileNotFoundError(f"File '{name}' not found.")
        return self.api.folder.download_file(file_info["id"])

    def _save(self, name, content):
        # Upload the file to Microsoft Graph
        full_path = self._get_full_path(name)
        parent_path = os.path.dirname(full_path)
        info = self.api.folder.get(parent_path, select=["id"])
        if not info:
            self.api.folder.create_path(parent_path)
            info = self.api.folder.get(parent_path, select=["id"])
        self.api.folder.upload_file(content, info["id"], name)
        return name

    def delete(self, name):
        # Delete the file from Microsoft Graph
        file_info = self._get_file_info(name)
        if not file_info:
            raise FileNotFoundError(f"File '{name}' not found.")
        self.api.folder.delete_file(file_info["id"])

    def exists(self, name):
        # Check if the file exists in Microsoft Graph
        return self._get_file_info(name, select=["id"]) is not None

    def get_valid_name(self, name: str) -> str:
        return name

    def url(self, name):
        # Get the public URL of the file
        file_info = self._get_file_info(name, select=["webUrl"])
        return file_info.get("webUrl") if file_info else None
