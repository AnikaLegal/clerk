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
    topic = models.CharField(max_length=32, choices=TOPIC_CHOICES, default="REPAIRS")
    questions = JSONField(encoder=DjangoJSONEncoder)
    answers = JSONField(encoder=DjangoJSONEncoder)
    num_answers = models.IntegerField(default=0)
    complete = models.BooleanField(default=False)
    # Tracks whether a Slack alert has been successfully sent.
    is_alert_sent = models.BooleanField(default=False)
    # Tracks whether the case data has been successfully sent.
    is_data_sent = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        """
        Populate num_answers.with any avalable answers
        """
        try:
            self.num_answers = len(self.answers)
        except TypeError:
            pass  # No length possible

        super().save(*args, **kwargs)
