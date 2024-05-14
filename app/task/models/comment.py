from django.db import models

from accounts.models import User
from core.models import TimestampedModel


class CommentType(models.TextChoices):
    SYSTEM = "SYSTEM", "System generated"
    USER = "USER", "User created"


class TaskComment(TimestampedModel):
    """
    A comment made on a task.
    """

    task = models.ForeignKey("task.Task", on_delete=models.CASCADE)
    type = models.CharField(max_length=32, choices=CommentType.choices)
    creator = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    text = models.TextField(blank=True, default="")

    class Meta:
        verbose_name = "comment"

