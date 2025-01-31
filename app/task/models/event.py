from accounts.models import User
from django.db import models
from django.utils import timezone


class TaskEventType(models.TextChoices):
    """
    The type of the event.
    """

    STATUS_CHANGE = "STATUS_CHANGE",


class TaskEvent(models.Model):
    type = models.CharField(max_length=32, choices=TaskEventType.choices)
    task = models.ForeignKey(
        "task.Task",
        on_delete=models.CASCADE,
        related_name="+",
    )
    # The user the task is assigned to.
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="+",
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "event"
