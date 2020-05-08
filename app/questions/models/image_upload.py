import hashlib
import os
import uuid

from django.db import models

from .timestamped import TimestampedModel


def get_s3_key(file_upload, filename):
    """
    Get S3 key for the file - use a hash of the file bytes to
    ensure that files are unique.
    """
    try:
        file = file_upload.image
    except AttributeError:
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
    A non-image document uploaded by a user.
    """

    UPLOAD_KEY = "file-uploads"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(upload_to=get_s3_key)


class ImageUpload(TimestampedModel):
    """
    An image uploaded by a user
    """

    UPLOAD_KEY = "image-uploads"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ImageField(upload_to=get_s3_key)
