import logging
import os
from datetime import datetime
from urllib.parse import quote

from django.core.cache import cache
from django.core.files.storage import Storage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from microsoft.endpoints import MSGraphAPI

logger = logging.getLogger(__name__)


class SimpleCache:
    def __init__(self, cache_prefix, timeout=None):
        self.cache_prefix = cache_prefix
        self.timeout = timeout

    def _get_key(self, key):
        # Quote the key to prevent Django cache key warnings.
        return f"{self.cache_prefix}:{quote(key)}"

    def get(self, key):
        key = self._get_key(key)
        logger.debug(f"Getting cache for key: {key}")
        return cache.get(key)

    def set(self, key, value, timeout=None):
        key = self._get_key(key)
        timeout = timeout or self.timeout
        logger.debug(f"Setting cache for key: {key} with timeout: {timeout}")
        cache.set(key, value, timeout=timeout)

    def delete(self, key):
        key = self._get_key(key)
        logger.debug(f"Deleting cache for key: {key}")
        cache.delete(key)


class MSGraphStorage(Storage):
    def __init__(self, cache_timeout=60, enable_directory_caching=False):
        self.api = MSGraphAPI()
        self.cache = SimpleCache(
            cache_prefix="ms_graph_file_info", timeout=cache_timeout
        )
        self.enable_directory_caching = enable_directory_caching
        logger.debug(
            f"Initialized MSGraphStorage with base_path: "
            f"cache_timeout: {cache_timeout}, "
            f"enable_directory_caching: {enable_directory_caching}"
        )

    def _cache_target_and_siblings(self, path):
        dir, _ = os.path.split(path)
        if not dir:
            logger.debug(f"No directory found for path: {path}")
            return

        info = self.api.folder.get(dir)
        if not info:
            logger.debug(f"No folder info found for directory: {dir}")
            return

        siblings = self.api.folder.get_children(dir)
        if not siblings:
            logger.debug(f"No siblings found for directory: {dir}")
            return

        for sibling in siblings:
            if sibling.get("folder"):
                logger.debug(f"Skipping folder: {sibling['name']}")
                continue
            name = sibling["name"]
            path = os.path.join(dir, name)
            logger.debug(f"Caching sibling: {path}")
            self.cache.set(path, sibling)

    def _get_file_info(self, path) -> dict | None:
        logger.debug(f"Getting file info for: {path}")
        info = self.cache.get(path)
        if info:
            logger.debug(f"Cache hit for file: {path}")
            return info

        if self.enable_directory_caching:
            logger.debug(
                f"Directory caching enabled. Caching target and siblings for: {path}"
            )
            self._cache_target_and_siblings(path)
            info = self.cache.get(path)
            if info:
                logger.debug(f"Cache hit after caching siblings for file: {path}")
                return info

        logger.debug(f"Cache miss. Fetching file info from API for: {path}")
        info = self.api.folder.get(path)
        if info:
            logger.debug(f"File info fetched from API for: {path}. Caching it.")
            self.cache.set(path, info)
        else:
            logger.debug(f"No file info found for: {path}")
        return info

    def _open(self, name, mode="rb"):
        logger.debug(f"Opening file: {name} with mode: {mode}")

        info = self._get_file_info(name)
        if not info:
            raise FileNotFoundError(f"File not found: {name}")

        file_name, content_type, bytes = self.api.folder.download_file(info["id"])
        logger.debug(f"File downloaded: {file_name}, content_type: {content_type}")

        return SimpleUploadedFile(
            name=os.path.basename(file_name),
            content=bytes,
            content_type=content_type,
        )

    def _save(self, name, content):
        logger.debug(f"Saving file: {name}")

        path, file_name = os.path.split(name)
        dir_info = self._get_file_info(path)
        if not dir_info:
            logger.debug(f"Folder not found. Creating path: {path}")
            self.api.folder.create_path(path)
            dir_info = self._get_file_info(path)
            if not dir_info:
                raise FileNotFoundError(f"Folder not found: {path}")

        file_info = self.api.folder.upload_file(content, dir_info["id"], file_name)
        if not file_info:
            raise Exception(f"Could not save file '{file_name}' to folder '{path}'")
        return os.path.join(path, file_info["name"])

    def delete(self, name):
        logger.debug(f"Deleting file: {name}")

        info = self._get_file_info(name)
        if info:
            self.api.folder.delete_file(info["id"])
            self.cache.delete(name)
            logger.debug(f"File deleted: {name}")

    def exists(self, name):
        logger.debug(f"Checking existence of file: {name}")
        return self._get_file_info(name) is not None

    def get_created_time(self, name: str) -> datetime:
        logger.debug(f"Getting created time for file: {name}")
        info = self._get_file_info(name)
        if not info:
            raise FileNotFoundError(f"File not found: {name}")
        return timezone.datetime.fromisoformat(info["createdDateTime"])

    def get_modified_time(self, name: str) -> datetime:
        logger.debug(f"Getting modified time for file: {name}")
        info = self._get_file_info(name)
        if not info:
            raise FileNotFoundError(f"File not found: {name}")
        return timezone.datetime.fromisoformat(info["lastModifiedDateTime"])

    def get_valid_name(self, name: str) -> str:
        logger.debug(f"Validating name: {name}")
        return name

    def is_name_available(self, name, max_length=None):
        # We don't check to see if file with the same name already exists here
        # because when that is the case the base storage code attempts to
        # generate another name but we want this handled by msgraph according to
        # the conflict resolution settings.
        exceeds_max_length = max_length and len(name) > max_length
        return not exceeds_max_length

    def size(self, name):
        logger.debug(f"Getting size for file: {name}")
        info = self._get_file_info(name)
        if not info:
            raise FileNotFoundError(f"File not found: {name}")
        return info["size"]

    def url(self, name):
        logger.debug(f"Getting URL for file: {name}")
        info = self._get_file_info(name)
        if not info:
            logger.warning(f"File not found: {name}")
            return ""
        return info["webUrl"]
