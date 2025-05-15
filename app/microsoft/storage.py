import os
from django.core.files.storage import Storage
from microsoft.endpoints import MSGraphAPI


class MSGraphStorage(Storage):
    def __init__(self, base_path):
        self.api = MSGraphAPI()
        self.base_path = base_path

    def _get_file_info(self, name, select=None):
        if ":" in name:
            path, name = name.split(":", 1)
            return self.api.folder.get_info_by_id(name, select)
        else:
            path = os.path.join(self.base_path, name)
            return self.api.folder.get(path, select)

    def _open(self, name, mode="rb"):
        pass

    def _save(self, name, content):
        head, tail = os.path.split(name)
        path = os.path.join(self.base_path, head)

        info = self.api.folder.get(path, select=["id"])
        if not info:
            self.api.folder.create_path(path)
            info = self.api.folder.get(path, select=["id"])

        info = self.api.folder.upload_file(content, info["id"], tail)
        return f"{head}:{info['id']}"

    def delete(self, name):
        pass

    def exists(self, name):
        return self._get_file_info(name, select=["id"]) is not None

    def get_valid_name(self, name: str) -> str:
        return name

    def url(self, name):
        info = self._get_file_info(name, select=["webUrl"])
        if not info:
            return None
        return info["webUrl"]
