from core.models import TimestampedModel
from django.db import models
from utils.uploads import get_s3_key


class TaskAttachment(TimestampedModel):
    UPLOAD_KEY = "task-attachments"

    task = models.ForeignKey(
        "task.Task",
        on_delete=models.CASCADE,
        related_name="attachments",
        related_query_name="attachment",
    )
    comment = models.ForeignKey(
        "task.TaskComment", on_delete=models.CASCADE, null=True, blank=True
    )
    file = models.FileField(upload_to=get_s3_key)
    content_type = models.CharField(max_length=128)

    class Meta:
        verbose_name = "attachment"