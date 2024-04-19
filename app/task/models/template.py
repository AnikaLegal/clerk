from django.db import models
from core.models.timestamped import TimestampedModel
from .trigger import TaskTrigger

class TaskTemplate(TimestampedModel):
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True, default="")
    trigger = models.ForeignKey(
        TaskTrigger,
        on_delete=models.CASCADE,
        related_name="templates",
        related_query_name="template",
    )

    class Meta:
        order_with_respect_to = "trigger"
        verbose_name = "template"