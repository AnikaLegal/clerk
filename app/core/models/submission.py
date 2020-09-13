import uuid

from django.db import models
from django.core.serializers.json import DjangoJSONEncoder

from .timestamped import TimestampedModel
from .client import Client


class CaseTopic:
    REPAIRS = "REPAIRS"
    RENT_REDUCTION = "RENT_REDUCTION"
    OTHER = "OTHER"


class Submission(TimestampedModel):
    """
    A submission by a client describing a specific issue.
    """

    TOPIC_CHOICES = (
        (CaseTopic.REPAIRS, CaseTopic.REPAIRS),
        (CaseTopic.RENT_REDUCTION, CaseTopic.RENT_REDUCTION),
        (CaseTopic.OTHER, CaseTopic.OTHER),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    topic = models.CharField(max_length=32, choices=TOPIC_CHOICES)
    answers = models.JSONField(encoder=DjangoJSONEncoder)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    complete = models.BooleanField(default=False)
    # Tracks whether a Slack alert has been successfully sent.
    is_alert_sent = models.BooleanField(default=False)
    # Tracks whether the case data has been successfully sent via email.
    is_data_sent = models.BooleanField(default=False)
    # Tracks whether the case data has been successfully sent to Actionstep.
    is_case_sent = models.BooleanField(default=False)
    # Tracks whether MailChimp reminder email has been successfully sent.
    is_reminder_sent = models.BooleanField(default=False)
