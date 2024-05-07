from django.db import models

from core.models import TimestampedModel, Issue
from .template import TaskTemplate, TaskType
from .trigger import TasksCaseRole


class TaskStatus(models.TextChoices):
    """
    The status of the task.
    """

    NOT_STARTED = "NOT_STARTED", "Not started"
    IN_PROGRESS = "IN_PROGRESS", "In progress"
    DONE = "DONE", "Done"
    NOT_DONE = "NOT_DONE", "Not done"


class Task(TimestampedModel):
    role = models.CharField(max_length=32, choices=TasksCaseRole.choices)
    template = models.ForeignKey(
        TaskTemplate, on_delete=models.PROTECT, blank=True, null=True
    )
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)

    type = models.CharField(max_length=32, choices=TaskType.choices)
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True, default="")
    status = models.CharField(
        max_length=32, choices=TaskStatus.choices, default=TaskStatus.NOT_STARTED
    )
