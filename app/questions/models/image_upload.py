import os
import uuid
import hashlib

from django.db import models

from .timestamped import TimestampedModel

UPLOAD_KEY = "image-uploads"


def get_s3_key(image_upload, filename):
    """
    Get S3 key for the photo - use a hash of the photo bytes to
    ensure that photos are unique.
    """
    if image_upload.image._file:
        img_bytes = image_upload.image._file.file.read()
        image_upload.image._file.file.seek(0)
        filename_base = hashlib.md5(img_bytes).hexdigest()
        _, filename_ext = os.path.splitext(filename)
        filename = filename_base + filename_ext.lower()

    return f"{UPLOAD_KEY}/{filename}"


class ImageUpload(TimestampedModel):
    """
    An image uploaded by a user
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ImageField(upload_to=get_s3_key)
