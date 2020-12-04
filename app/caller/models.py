from django.db import models
from core.models.timestamped import TimestampedModel
from core.models.issue import Issue


class Call(TimestampedModel):
    """
    A call made to our Twilio number
    """

    phone_number = models.CharField(max_length=32)
    topic = models.CharField(max_length=32, choices=Issue.TOPIC_CHOICES)
    requires_callback = models.BooleanField(default=False)
    number_callbacks = models.IntegerField(default=0)
