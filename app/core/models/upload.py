import hashlib
import os
import uuid

from django.conf import settings
from django.core.files.storage import storages
from django.db import models

from .issue import Issue
from .timestamped import TimestampedModel


def get_s3_key(file_upload, filename):
    """
    Get S3 key for the file - use a hash of the file bytes to
    ensure that files are unique and that filenames are not easily guessed.
    """
    file = file_upload.file
    if file._file:
        img_bytes = file._file.file.read()
        file._file.file.seek(0)
        filename_base = hashlib.md5(img_bytes).hexdigest()
        _, filename_ext = os.path.splitext(filename)
        filename = filename_base + filename_ext.lower()

    return f"{file_upload.UPLOAD_KEY}/{filename}"


class FileUpload(TimestampedModel):
    """
    An image or document uploaded by a user as a part of a issue.
    """

    UPLOAD_KEY = "file-uploads"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(
        upload_to=get_s3_key, storage=storages[settings.FILE_UPLOAD_STORAGE]
    )
    issue = models.ForeignKey(Issue, on_delete=models.SET_NULL, null=True, blank=True)
