import uuid

from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models

from .timestamped import TimestampedModel


class Submission(TimestampedModel):
    """
    A form submission
    """

    TOPIC_CHOICES = (("REPAIRS", "REPAIRS"), ("COVID", "COVID"))

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    complete = models.BooleanField(default=False)
    topic = models.CharField(max_length=32, choices=TOPIC_CHOICES, default="REPAIRS")
    questions = JSONField(encoder=DjangoJSONEncoder)
    answers = JSONField(encoder=DjangoJSONEncoder)
