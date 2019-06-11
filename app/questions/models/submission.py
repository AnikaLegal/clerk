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
    data = JSONField(encoder=DjangoJSONEncoder)
    complete = models.BooleanField(default=False)
