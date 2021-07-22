from django.db import models
from django.utils.text import slugify


class EmailState:
    DRAFT = "DRAFT"
    READY_TO_SEND = "READY_TO_SEND"
    SENT = "SENT"
    RECEIVED = "RECEIVED"


STATE_CHOICES = (
    (EmailState.DRAFT, "Draft"),
    (EmailState.READY_TO_SEND, "Ready to send"),
    (EmailState.SENT, "Sent"),
    (EmailState.RECEIVED, "Received"),
)


class Email(models.Model):

    from_addr = models.EmailField()
    to_addr = models.EmailField()
    to_addrs = models.TextField()
    cc_addrs = models.TextField(default="")
    subject = models.CharField(max_length=1024)
    state = models.CharField(max_length=32, choices=STATE_CHOICES)
    text = models.TextField()
    html = models.TextField(default="")


def get_s3_key(email, filename):
    fn = slugify(filename)
    return f"{email.UPLOAD_KEY}/{fn}"


# FIXME: Configure so S3 bucket cannot be publicly read from
class EmailAttachment(models.Model):
    UPLOAD_KEY = "email-attachments"

    email = models.ForeignKey(Email, on_delete=models.SET_NULL, null=True, blank=True)
    file = models.FileField(upload_to=get_s3_key)
    mimetype = models.CharField(max_length=128)
