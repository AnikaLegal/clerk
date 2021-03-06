import uuid

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from .timestamped import TimestampedModel


class CaseTopic:
    REPAIRS = "REPAIRS"
    COVID = "COVID"


class Submission(TimestampedModel):
    """
    A form submission
    """

    TOPIC_CHOICES = (
        (CaseTopic.REPAIRS, CaseTopic.REPAIRS),
        (CaseTopic.COVID, CaseTopic.COVID),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    topic = models.CharField(max_length=32, choices=TOPIC_CHOICES, default="REPAIRS")
    questions = models.JSONField(encoder=DjangoJSONEncoder)
    answers = models.JSONField(encoder=DjangoJSONEncoder)
    num_answers = models.IntegerField(default=0)
    complete = models.BooleanField(default=False)
    # Tracks whether a Slack alert has been successfully sent.
    is_alert_sent = models.BooleanField(default=False)
    # Tracks whether the case data has been successfully sent via email.
    is_data_sent = models.BooleanField(default=False)
    # Tracks whether the case data has been successfully sent to Actionstep.
    is_case_sent = models.BooleanField(default=False)
    # Tracks whether MailChimp reminder email has been successfully sent.
    is_reminder_sent = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        """
        Populate num_answers.with any avalable answers
        """
        try:
            self.num_answers = len(self.answers)
        except TypeError:
            pass  # No length possible

        super().save(*args, **kwargs)
