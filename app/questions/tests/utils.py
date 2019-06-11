import io

from django.core.files.uploadedfile import InMemoryUploadedFile

TINY_PNG = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\tpHYs\x00\x00\x0e\xc4\x00\x00\x0e\xc4\x01\x95+\x0e\x1b\x00\x00\x00\x19tEXtSoftware\x00gnome-screenshot\xef\x03\xbf>\x00\x00\x00\rIDAT\x08\x99c```\xf8\x0f\x00\x01\x04\x01\x00}\xb2\xc8\xdf\x00\x00\x00\x00IEND\xaeB`\x82"


def drf_isoformat(datetime):
    iso_str = datetime.isoformat()
    if iso_str.endswith("+00:00"):
        iso_str = iso_str[:-6] + "Z"

    return iso_str


def get_dummy_file(name):
    f = io.BytesIO(TINY_PNG)
    return InMemoryUploadedFile(f, None, name, "image/png", len(TINY_PNG), None)

