import uuid

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models

from core.models.timestamped import TimestampedModel
from core.models.issue import CaseTopic


class ClosedContact(TimestampedModel):
    """
    A contact from when the intake form is closed.
    """

    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    topic = models.CharField(max_length=32, choices=CaseTopic.CHOICES)


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
    comments = models.CharField(max_length=255, default="", blank=True)

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
