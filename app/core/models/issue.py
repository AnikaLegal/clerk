import uuid

from django.db import models
from django.core.serializers.json import DjangoJSONEncoder

from .timestamped import TimestampedModel
from .client import Client


class CaseTopic:
    REPAIRS = "REPAIRS"
    RENT_REDUCTION = "RENT_REDUCTION"
    OTHER = "OTHER"


class Issue(TimestampedModel):
    """
    A client's specific issue.
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
    # Tracks whether the client has finished answering all questions.
    is_answered = models.BooleanField(default=False)
    # Tracks whether the client has submitted their issue to Anika for help.
    is_submitted = models.BooleanField(default=False)
    # Tracks whether a Slack alert has been successfully sent.
    is_alert_sent = models.BooleanField(default=False)
    # Tracks whether the case data has been successfully sent to Actionstep.
    is_case_sent = models.BooleanField(default=False)
