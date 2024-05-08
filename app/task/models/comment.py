from django.db import models
from accounts.models import User

from core.models import TimestampedModel
from .task import Task


class CommentType(models.TextChoices):
    # TODO
    pass


class TaskComment(TimestampedModel):
    """
    A comment made on a task.
    """
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    type = models.CharField(max_length=32, choices=CommentType.choices)
    creator = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    text = models.TextField(blank=True, default="")