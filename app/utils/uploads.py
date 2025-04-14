import hashlib
from django.utils.text import slugify

"""
63: max s3 bucket name size.
1: file path separator between bucket name & object key.
1024: max s3 object key length.
"""
FILE_FIELD_MAX_LENGTH_S3 = 63 + 1 + 1024


def get_s3_key(model, filename: str):
    """
    Get S3 key for the file - use a hash of the file bytes to
    ensure that files are unique and that filenames are not easily guessed.

    Assumes model has a FileField named 'file' and an attribute UPLOAD_KEY.
    """
    file = model.file
    file_bytes = file.read()
    file.seek(0)
    file_hash = hashlib.md5(file_bytes).hexdigest()
    new_filename = ".".join([slugify(p) for p in filename.split(".")]).lower()
    return f"{model.UPLOAD_KEY}/{file_hash}/{new_filename}"
