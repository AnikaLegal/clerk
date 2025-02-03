from accounts.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models, transaction
from django.urls import reverse
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
    note_html = models.TextField(null=True)
    created_at = models.DateTimeField(default=timezone.now)

    @transaction.atomic
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        TaskActivity.objects.create(content_object=self)

    def get_desc_html(self):
        html = ""
        if self.type == TaskEventType.STATUS_CHANGE:
            html = self._get_status_change_html()
        return html

    def _get_status_change_html(self):
        user = self.user
        user_url = reverse("account-detail", args=(user.id,))

        prev_status = self.data.get("prev_status")
        prev_status = TaskStatus[prev_status].label

        next_status = self.data.get("next_status")
        next_status = TaskStatus[next_status].label

        return (
            f'<a href="{user_url}">{user.first_name}</a> '
            + f"changed status from <strong>{prev_status}</strong> "
            + f"to <strong>{next_status}</strong>"
        )

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
            note_html=note,
        )
