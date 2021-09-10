from django.db import models
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.postgres.fields import ArrayField

from accounts.models import User
from core.models import Issue
from utils.uploads import get_s3_key


class EmailState:
    DRAFT = "DRAFT"
    READY_TO_SEND = "READY_TO_SEND"
    SENT = "SENT"
    RECEIVED = "RECEIVED"
    INGESTED = "INGESTED"
    INGEST_FAILURE = "INGEST_FAILURE"


STATE_CHOICES = (
    (EmailState.DRAFT, "Draft"),
    (EmailState.READY_TO_SEND, "Ready to send"),
    (EmailState.SENT, "Sent"),
    (EmailState.RECEIVED, "Received"),
    (EmailState.INGESTED, "Ingested"),
    (EmailState.INGEST_FAILURE, "Ingest failed"),
)


class Email(models.Model):

    from_address = models.EmailField(default="")
    to_address = models.EmailField(default="", blank=True)
    cc_addresses = ArrayField(models.EmailField(), default=list, blank=True)
    subject = models.CharField(max_length=1024, default="")
    state = models.CharField(max_length=32, choices=STATE_CHOICES)
    text = models.TextField(default="", blank=True)
    html = models.TextField(default="", blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    issue = models.ForeignKey(Issue, blank=True, null=True, on_delete=models.PROTECT)
    sender = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.PROTECT, related_name="sent_email"
    )
    received_data = models.JSONField(encoder=DjangoJSONEncoder)

    # Actionstep ID
    actionstep_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.pk}: {self.subject}"

    def get_received_note_text(self):
        return "Email received"

    def get_sent_note_text(self):
        return "Email sent"


# FIXME: Configure so S3 bucket cannot be publicly read from?
class EmailAttachment(models.Model):
    UPLOAD_KEY = "email-attachments"

    email = models.ForeignKey(Email, on_delete=models.PROTECT, null=True, blank=True)
    file = models.FileField(upload_to=get_s3_key)
    content_type = models.CharField(max_length=128)
    created_at = models.DateTimeField(default=timezone.now)
    actionstep_id = models.IntegerField(blank=True, null=True)
