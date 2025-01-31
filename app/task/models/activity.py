from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone


class TaskActivity(models.Model):
    task = models.ForeignKey(
        "task.Task",
        on_delete=models.CASCADE,
        related_name="activities",
        related_query_name="activity",
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    created_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        self.task_id = self.content_object.task_id
        if not self.created_at:
            try:
                self.created_at = self.content_object.created_at
            except AttributeError:
                self.created_at = timezone.now()
        super().save(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]
        verbose_name = "activity"
        verbose_name_plural = "activities"
