import os
from urllib.parse import quote

from django.core.files.storage import Storage
from django.core.files.uploadedfile import SimpleUploadedFile
from microsoft.endpoints import MSGraphAPI

from django.core.cache import cache


class SimpleCache:
    def __init__(self, cache_prefix, timeout=None):
        self.cache_prefix = cache_prefix
        self.timeout = timeout

    def _get_key(self, key):
        return f"{self.cache_prefix}:{key}"

    def get(self, key):
        key = self._get_key(key)
        return cache.get(key)

    def set(self, key, value, timeout=None):
        key = self._get_key(key)
        cache.set(key, value, timeout=self.timeout if timeout is None else timeout)

    def delete(self, key):
        key = self._get_key(key)
        cache.delete(key)


class MSGraphStorage(Storage):
    def __init__(
        self, base_path: str, cache_timeout=60, enable_directory_caching=False
    ):
        self.api = MSGraphAPI()
        self.base_path = base_path
        self.cache = SimpleCache(
            cache_prefix="ms_graph_file_info", timeout=cache_timeout
        )
        self.enable_directory_caching = enable_directory_caching

    def _get_full_path(self, name):
        return os.path.join(self.base_path, name)

    def _cache_target_and_siblings(self, name):
        path = self._get_full_path(name)
        dir, _ = os.path.split(path)
        if not dir:
            return
        info = self.api.folder.get(dir)
        if not info:
            return
        siblings = self.api.folder.get_children(dir)
        if not siblings:
            return
        for sibling in siblings:
            name = quote(sibling["name"])
            path = os.path.join(dir, name)
            self.cache.set(path, sibling)

    def _get_file_info(self, name) -> dict | None:
        # Check if the info is in the cache
        path = self._get_full_path(name)
        info = self.cache.get(path)
        if info:
            return info

        if self.enable_directory_caching:
            # This is a performance optimisation to avoid hitting the API for
            # every file access. We attempt to get & cache the file info for
            # each file in the same directory as the target file with one API
            # call.
            self._cache_target_and_siblings(name)
            info = self.cache.get(path)
            if info:
                return info

        info = self.api.folder.get(path)
        if info:
            self.cache.set(path, info)
        return info

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
        dir, _ = os.path.split(name)
        info = self._get_file_info(dir)
        if not info:
            path = self._get_full_path(dir)
            self.api.folder.create_path(path)
            info = self._get_file_info(dir)
        if not info:
            raise FileNotFoundError(f"Folder {dir} not found")
        self.api.folder.upload_file(content, info["id"])
        return name

    def delete(self, name):
        info = self._get_file_info(name)
        if info:
            self.api.folder.delete_file(info["id"])
            path = self._get_full_path(name)
            self.cache.delete(path)

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
