from core.models import TimestampedModel
from django.db import models


class TaskGroup(TimestampedModel):
    name = models.CharField(max_length=64)

    class Meta:
        verbose_name = "group"
