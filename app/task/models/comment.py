from accounts.models import User
from core.models import TimestampedModel
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models, transaction

from .activity import TaskActivity


class TaskComment(TimestampedModel):
    """
    A comment made on a task.
    """

    task = models.ForeignKey(
        "task.Task",
        on_delete=models.CASCADE,
        related_name="+",
    )
    activity = GenericRelation(TaskActivity)
    creator = models.ForeignKey(User, on_delete=models.PROTECT)
    text = models.TextField()

    @transaction.atomic
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        TaskActivity.objects.create(content_object=self)

    class Meta:
        verbose_name = "comment"
