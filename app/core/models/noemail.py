import uuid

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models

from core.models.timestamped import TimestampedModel


class NoEmailAdmin(TimestampedModel):
    """
    A no email submission
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.JSONField(encoder=DjangoJSONEncoder)
    phone_number = models.JSONField(encoder=DjangoJSONEncoder)
    # Whether we successfully processed this submission.
    is_processed = models.BooleanField(default=False)
    # Tracks whether MailChimp reminder email has been successfully sent.
    is_reminder_sent = models.BooleanField(default=False)
