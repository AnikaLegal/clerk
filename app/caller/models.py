from django.db import models

from core.models.issue import CaseTopic
from core.models.timestamped import TimestampedModel


class Call(TimestampedModel):
    """
    A call made to our Twilio number
    """

    phone_number = models.CharField(max_length=32)
    topic = models.CharField(max_length=32, choices=CaseTopic.CHOICES)
    requires_callback = models.BooleanField(default=False)
    number_callbacks = models.IntegerField(default=0)
    comments = models.CharField(max_length=256, blank=True, default="")
