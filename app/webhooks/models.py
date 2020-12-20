import uuid

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models

from core.models.timestamped import TimestampedModel


class WebflowContact(TimestampedModel):
    """
    A client contact form submission from anikalegal.com
    """

    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    referral = models.CharField(max_length=255, default="", blank=True)
    requires_callback = models.BooleanField(default=True)
    number_callbacks = models.IntegerField(default=0)

    # Tracks whether a Slack alert has been successfully sent.
    is_alert_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.pk} {self.email}"


class JotformSubmission(TimestampedModel):
    """
    A submission from a Jotform survey
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form_name = models.CharField(max_length=128)
    answers = models.JSONField(encoder=DjangoJSONEncoder)
