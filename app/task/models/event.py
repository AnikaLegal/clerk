from accounts.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models, transaction
from django.utils import timezone

from .activity import TaskActivity
from .task import TaskStatus


class TaskEventType(models.TextChoices):
    """
    The type of the event.
    """

    STATUS_CHANGE = "STATUS_CHANGE"


class TaskEvent(models.Model):
    class Meta:
        verbose_name = "event"

    type = models.TextField(choices=TaskEventType.choices, null=False, blank=False)
    task = models.ForeignKey(
        "task.Task",
        on_delete=models.CASCADE,
        related_name="+",
    )
    activity = GenericRelation(TaskActivity)
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="+",
    )
    data = models.JSONField()
    note = models.TextField(null=True)
    created_at = models.DateTimeField(default=timezone.now)

    @transaction.atomic
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        TaskActivity.objects.create(content_object=self)

    def get_html(self):
        html = ""
        if self.type == TaskEventType.STATUS_CHANGE:
            html = self._get_status_change_html()
        return html

    def _get_status_change_html(self):
        user = self.user

        prev_status = self.data.get("prev_status")
        prev_status = TaskStatus[prev_status].label

        next_status = self.data.get("next_status")
        next_status = TaskStatus[next_status].label

        html = f"{user.first_name} changed status from {prev_status} to {next_status}"
        if self.note:
            html += f" with comment: {self.note}"
        return html

    @staticmethod
    def create_status_change(task, user, prev_status, next_status, note=None):
        return TaskEvent.objects.create(
            type=TaskEventType.STATUS_CHANGE,
            task=task,
            user=user,
            data={
                "prev_status": prev_status,
                "next_status": next_status,
            },
            note=note,
        )
