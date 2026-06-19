import math

# SendGrid rejects any message whose total size exceeds 30MB. That total is
# measured AFTER attachments are base64 encoded (which inflates them by ~33%).
# Leave a margin below 30MB for MIME headers / multipart boundaries.
MAX_EMAIL_SIZE_BYTES = 29 * 1024 * 1024


def base64_size(num_bytes: int) -> int:
    """Byte length of `num_bytes` once base64 encoded."""
    return math.ceil(num_bytes / 3) * 4


def get_email_payload_size(text: str, html: str, attachments) -> int:
    """
    Approximate the SendGrid payload size of an email: the body plus all
    attachments after base64 encoding.
    """
    size = len((text or "").encode("utf-8")) + len((html or "").encode("utf-8"))
    for att in attachments:
        # `file.size` reads object metadata from storage (e.g. an S3 HEAD
        # request) without downloading the file.
        size += base64_size(att.file.size)
    return size


def format_size(num_bytes: int) -> str:
    """Human-readable size for user-facing messages, e.g. '21.7MB'."""
    return f"{num_bytes / 1024 / 1024:.1f}MB"
