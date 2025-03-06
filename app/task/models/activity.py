from core.models import TimestampedModel
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class TaskActivity(TimestampedModel):
    class Meta:
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]
        verbose_name = "activity"
        verbose_name_plural = "activities"

    task = models.ForeignKey(
        "task.Task",
        on_delete=models.CASCADE,
        related_name="activities",
        related_query_name="activity",
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    def save(self, *args, **kwargs):
        if not self.task_id:
            self.task_id = self.content_object.task_id

        super().save(*args, **kwargs)

        try:
            self.created_at = self.content_object.created_at
        except AttributeError:
            pass
        try:
            self.modified_at = self.content_object.modified_at
        except AttributeError:
            pass
