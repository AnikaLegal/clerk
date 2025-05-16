import os

from django.core.files.storage import Storage
from django.core.files.uploadedfile import SimpleUploadedFile
from microsoft.endpoints import MSGraphAPI


class MSGraphStorage(Storage):
    def __init__(self, base_path: str):
        self.api = MSGraphAPI()
        self.base_path = base_path

    def _get_full_path(self, path):
        return os.path.join(self.base_path, path)

    def _get_file_info(self, name):
        path = self._get_full_path(name)
        return self.api.folder.get(path)

    def _open(self, name, mode="rb"):
        info = self._get_file_info(name)
        if not info:
            raise FileNotFoundError(f"File {name} not found")
        file_name, content_type, bytes = self.api.folder.download_file(info["id"])

        return SimpleUploadedFile(
            name=os.path.basename(file_name),
            content=bytes,
            content_type=content_type,
        )

    def _save(self, name, content):
        dir, file_name = os.path.split(name)
        info = self._get_file_info(dir)
        if not info:
            path = self._get_full_path(dir)
            self.api.folder.create_path(path)
            info = self._get_file_info(dir)
        if not info:
            raise FileNotFoundError(f"Folder {dir} not found")
        self.api.folder.upload_file(content, info["id"], file_name)
        return name

    def delete(self, name):
        info = self._get_file_info(name)
        if info:
            self.api.folder.delete_file(info["id"])

    def exists(self, name):
        return self._get_file_info(name) is not None

    def get_valid_name(self, name: str) -> str:
        return name

    def size(self, name):
        info = self._get_file_info(name)
        if not info:
            raise FileNotFoundError(f"File {name} not found")
        return info["size"]

    def url(self, name):
        info = self._get_file_info(name)
        if not info:
            return ""
        return info["webUrl"]
