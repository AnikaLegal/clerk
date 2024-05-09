from django.db import models

from accounts.models import User
from core.models import TimestampedModel, Issue
from .template import TaskTemplate, TaskType


class TaskStatus(models.TextChoices):
    """
    The status of the task.
    """

    NOT_STARTED = "NOT_STARTED", "Not started"
    IN_PROGRESS = "IN_PROGRESS", "In progress"
    DONE = "DONE", "Done"
    NOT_DONE = "NOT_DONE", "Not done"


class Task(TimestampedModel):
    type = models.CharField(max_length=32, choices=TaskType.choices)
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True, default="")
    status = models.CharField(
        max_length=32, choices=TaskStatus.choices, default=TaskStatus.NOT_STARTED
    )
    is_open = models.BooleanField(default=True)

    # The issue to which the task relates.
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    # The original assignee.
    owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")
    # The current assignee.
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="+",
    )
    # If the task was created by the system then this refers to the template
    # used to create the task.
    template = models.ForeignKey(
        TaskTemplate, on_delete=models.PROTECT, blank=True, null=True
    )

    def save(self, *args, **kwargs):
        if not self.owner_id:
            self.owner = self.assigned_to

        if self.status in [TaskStatus.DONE, TaskStatus.NOT_DONE]:
            self.is_open = False
        else:
            self.is_open = True

        super().save(*args, **kwargs)


