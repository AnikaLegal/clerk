import uuid

from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models

from .timestamped import TimestampedModel


class Submission(TimestampedModel):
    """
    A form submission
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    complete = models.BooleanField(default=False)
    questions = JSONField(encoder=DjangoJSONEncoder)
    answers = JSONField(encoder=DjangoJSONEncoder)
