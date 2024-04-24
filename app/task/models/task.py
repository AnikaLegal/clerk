from django.db import models
from core.models import TimestampedModel, Issue
from .template import TaskTemplate


class TaskStatus(models.TextChoices):
    """
    The status of the task.
    """

    NOT_STARTED = "NOT_STARTED", "Not started"
    IN_PROGRESS = "IN_PROGRESS", "In progress"
    DONE = "DONE", "Done"
    NOT_DONE = "NOT_DONE", "Not done"


class Task(TimestampedModel):
    template = models.ForeignKey(TaskTemplate, on_delete=models.PROTECT)
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=32, choices=TaskStatus.choices, default=TaskStatus.NOT_STARTED
    )

    # assigned_to =
