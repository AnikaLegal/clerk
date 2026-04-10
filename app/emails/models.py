import hashlib
import json
import re

import psycopg2
from accounts.models import User
from core.models import CaseTopic, Issue, TimestampedModel
from django.contrib.postgres.fields import ArrayField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import IntegrityError, models
from django.utils import timezone
from django.utils.text import slugify
from utils.uploads import FILE_FIELD_MAX_LENGTH_S3, get_s3_key


class DuplicateEmailDataError(Exception):
    def __init__(self, message, hash):
        self.message = message
        self.hash = hash
        super().__init__(self.message)

    def __str__(self):
        message = super().__str__()
        message += f", hash: {self.hash}"
        return message


class EmailState:
    DRAFT = "DRAFT"
    READY_TO_SEND = "READY_TO_SEND"
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    DELIVERY_FAILURE = "DELIVERY_FAILURE"
    SAVING = "SAVING"
    RECEIVED = "RECEIVED"
    INGESTED = "INGESTED"
    INGEST_FAILURE = "INGEST_FAILURE"


STATE_CHOICES = (
    (EmailState.DRAFT, "Draft"),
    (EmailState.READY_TO_SEND, "Ready to send"),
    (EmailState.SENT, "Sent"),
    (EmailState.DELIVERED, "Delivered"),
    (EmailState.DELIVERY_FAILURE, "Delivery failed"),
    (EmailState.SAVING, "Saving"),
    (EmailState.RECEIVED, "Received"),
    (EmailState.INGESTED, "Ingested"),
    (EmailState.INGEST_FAILURE, "Ingest failed"),
)


class Email(models.Model):
    from_address = models.EmailField(default="")
    to_address = models.EmailField(default="", blank=True)
    cc_addresses = ArrayField(models.EmailField(), default=list, blank=True)
    subject = models.CharField(max_length=1024, default="")
    thread_name = models.SlugField(max_length=1024, default="", blank=True)
    state = models.CharField(max_length=32, choices=STATE_CHOICES)
    text = models.TextField(default="", blank=True)
    html = models.TextField(default="", blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    processed_at = models.DateTimeField(blank=True, null=True)
    issue = models.ForeignKey(Issue, blank=True, null=True, on_delete=models.PROTECT)
    sender = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.PROTECT, related_name="sent_email"
    )
    received_data = models.JSONField(encoder=DjangoJSONEncoder, null=True, blank=True)
    received_data_hash = models.CharField(unique=True, null=True, blank=True)

    # Sendgrid Email ID
    sendgrid_id = models.CharField(max_length=128, blank=True, default="")

    # Tracks whether an alert has been successfully sent.
    is_alert_sent = models.BooleanField(default=False)

    # Actionstep ID
    actionstep_id = models.IntegerField(blank=True, null=True)

    def save(self, *args, **kwargs):
        self.thread_name = slugify(
            re.sub(r"re\s*:\s*", "", self.subject, flags=re.IGNORECASE)
        )

        # Hash contents of received_data field.
        if self.state == EmailState.SAVING and self.received_data:
            self.received_data_hash = hashlib.sha256(
                json.dumps(self.received_data, sort_keys=True).encode()
            ).hexdigest()

        # Catch unique violation error for received_data_hash and convert to
        # something that is easier to use elsewhere.
        try:
            super().save(*args, **kwargs)
        except IntegrityError as e:
            if (
                isinstance(e.__cause__, psycopg2.errors.UniqueViolation)
                and isinstance(e.__cause__.diag, psycopg2.extensions.Diagnostics)
                and e.__cause__.diag.constraint_name is not None
                and "received_data_hash" in e.__cause__.diag.constraint_name
            ):
                raise DuplicateEmailDataError(
                    "Duplicate email rejected", self.received_data_hash
                ) from e
            # Just re-raise if it is a different error.
            raise

    def __str__(self):
        return f"{self.pk}: {self.subject}"

    def get_received_note_text(self):
        return "Email received"

    def get_sent_note_text(self):
        return "Email sent"

    def check_permission(self, user: User) -> bool:
        """
        Returns True if the user has object level permission to access this
        instance.
        """
        return self.issue is not None and (
            self.issue.paralegal == user or self.issue.lawyer == user
        )


class EmailTemplate(TimestampedModel):
    name = models.CharField(max_length=64, db_collation="natural")
    topic = models.CharField(
        max_length=32, choices=(("GENERAL", "General"), *CaseTopic.CHOICES)
    )
    text = models.TextField(default="", blank=True)
    subject = models.CharField(max_length=1024, default="")


class SharepointState(models.TextChoices):
    NOT_UPLOADED = "NOT_UPLOADED", "Not uploaded"
    UPLOADING = "UPLOADING", "Uploading"
    UPLOADED = "UPLOADED", "Uploaded"


# FIXME: Configure so S3 bucket cannot be publicly read from?
class EmailAttachment(models.Model):
    UPLOAD_KEY = "email-attachments"

    email = models.ForeignKey(
        Email,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="attachments",
    )
    file = models.FileField(upload_to=get_s3_key, max_length=FILE_FIELD_MAX_LENGTH_S3)
    content_type = models.CharField(max_length=128)
    created_at = models.DateTimeField(default=timezone.now)
    actionstep_id = models.IntegerField(blank=True, null=True)
    sharepoint_state = models.CharField(
        max_length=16,
        default=SharepointState.NOT_UPLOADED,
        choices=SharepointState.choices,
    )

    def check_permission(self, user: User) -> bool:
        """
        Returns True if the user has object level permission to access this instance.
        """
        return (
            self.email is not None
            and self.email.issue is not None
            and (self.email.issue.paralegal == user or self.email.issue.lawyer == user)
        )
