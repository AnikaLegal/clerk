import uuid

from django.db import models
from django.core.serializers.json import DjangoJSONEncoder

from core.models.timestamped import TimestampedModel


class Submission(TimestampedModel):
    """
    A form submission
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    answers = models.JSONField(encoder=DjangoJSONEncoder)
    # Whether this submission was completed by the client.
    is_complete = models.BooleanField(default=False)
    # Whether we successfully processed this submission.
    is_processed = models.BooleanField(default=False)
    # Tracks whether MailChimp reminder email has been successfully sent.
    is_reminder_sent = models.BooleanField(default=False)
