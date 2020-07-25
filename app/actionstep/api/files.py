import logging
from urllib.parse import urljoin

import requests

from .base import BaseEndpoint

FILE_CHUNK_BYTES = 5242880

logger = logging.getLogger(__file__)


class FileEndpoint(BaseEndpoint):
    """
    Endpoint for attaching files to Actions.
    https://actionstep.atlassian.net/wiki/spaces/API/pages/18251961/Action+Documents
    """

    resource = "actiondocuments"

    def __init__(self, *args, **kwargs):
        self.file_upload = FileUploadEndpoint(*args, **kwargs)
        self.folders = FolderEndpoint(*args, **kwargs)
        super().__init__(*args, **kwargs)

    def upload(self, filename: str, file_bytes: bytes):
        """
        Upload a file to Actionstep.
        {
            "id": "qwsqswqsqw",
            "status" : "Uploaded",
        }
        """
        return self.file_upload.create(filename, file_bytes)

    def attach(self, filename: str, file_id: str, action_id: str, foldername=None):
        """
        Attach a file to an Action
        """
        links = {"action": action_id}
        if foldername:
            folder_data = self.folders.get(foldername, action_id)
            links["folder"] = folder_data["id"]

        return super().create({"name": filename, "file": file_id, "links": links})


class FolderEndpoint(BaseEndpoint):
    """
    Endpoint for Action folders.
    https://actionstep.atlassian.net/wiki/spaces/API/pages/21135480/Action+Folders
    """

    resource = "actionfolders"

    def get(self, foldername: str, action_id: str):
        return super().get({"name": foldername, "action": action_id})


class FileUploadEndpoint(BaseEndpoint):
    """
    Endpoint for uploading/downloading files.
    https://actionstep.atlassian.net/wiki/spaces/API/pages/21135509/Files
    https://actionstep.atlassian.net/wiki/spaces/API/pages/12025904/Requests#Requests-UploadingFiles
    """

    resource = "files"

    def create(self, filename: str, file_bytes: bytes):
        chunk_size = FILE_CHUNK_BYTES
        byte_chunks = [
            file_bytes[i : i + chunk_size] for i in range(0, len(file_bytes), chunk_size)
        ]
        part_count = len(byte_chunks)
        file_id = None
        headers = {**self.headers}
        del headers["Content-Type"]

        logger.info("Uploading %s to Actionstep", filename)
        for idx, chunk_bytes in enumerate(byte_chunks):
            url = urljoin(self.url + "/", file_id) if file_id else self.url
            params = {"part_count": part_count, "part_number": idx + 1}
            files = {"file": (filename, chunk_bytes)}
            resp = requests.post(url, files=files, params=params, headers=headers)
            resp_data = self._handle_json_response(url, resp)
            file_data = resp_data["files"]
            file_id = file_data["id"]

        assert file_data["status"] == "Uploaded", f"File {file_id} not fully uploaded."
        return resp_data["files"]
