import os
from django.core.files.storage import Storage
from microsoft.endpoints import MSGraphAPI


class MSGraphStorage(Storage):
    def __init__(self, base_path: str):
        self.api = MSGraphAPI()
        self.base_path = "/" + base_path.lstrip("/")

    def _get_full_path(self, path):
        return os.path.join(self.base_path, path)

    def _check_path(self, info: dict, path: str):
        parent_path = info.get("parentReference", {}).get("path")
        if parent_path:
            parent_path = parent_path.split(":")[-1]
            if path == parent_path:
                return
        raise PermissionError("Access denied")

    def _get_file_info(self, name):
        path = self._get_full_path(name)
        return self.api.folder.get(path)

    def _save(self, name, content):
        head, tail = os.path.split(name)
        info = self._get_file_info(head)
        if not info:
            path = self._get_full_path(head)
            self.api.folder.create_path(path)
            info = self._get_file_info(head)

        info = self.api.folder.upload_file(content, info["id"], tail)
        return f"{head}:{info['id']}"

    def delete(self, name):
        info = self._get_file_info(name)
        if info:
            self.api.folder.delete_file(info["id"])

    def exists(self, name):
        return self._get_file_info(name) is not None

    def get_valid_name(self, name: str) -> str:
        return name

    def url(self, name):
        info = self._get_file_info(name)
        if not info:
            return ""
        return info["webUrl"]
