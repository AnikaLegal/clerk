from django.db import models
from core.models import TimestampedModel
from .trigger import TaskTrigger


class TaskType(models.TextChoices):
    """
    The type of the task.
    """

    CHECK = "CHECK", "Check for conflict/eligibility"
    CONTACT = "CONTACT", "Contact client or other party"
    DRAFT = "DRAFT", "Draft document or advice"
    REVIEW = "REVIEW", "Review document or advice"
    SEND = "SEND", "Send document or advice"
    OTHER = "OTHER", "Other"


class TaskTemplate(TimestampedModel):
    type = models.CharField(max_length=32, choices=TaskType.choices)
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