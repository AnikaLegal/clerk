import logging

from accounts.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone

from .activity import TaskActivity
from .task import Task, TaskStatus

logger = logging.getLogger(__name__)


class TaskEventType(models.TextChoices):
    """
    The type of the event.
    """

    REASSIGN = "REASSIGN"
    RESUME = "RESUME"
    STATUS_CHANGE = "STATUS_CHANGE"
    SUSPEND = "SUSPEND"


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
        try:
            if self.type == TaskEventType.STATUS_CHANGE:
                html = self._get_status_change_html()
            elif self.type == TaskEventType.SUSPEND:
                html = self._get_suspend_html()
            elif self.type == TaskEventType.REASSIGN:
                html = self._get_reassign_html()
            elif self.type == TaskEventType.RESUME:
                html = self._get_resume_html()
        except Exception:
            logger.exception(
                "Could not generate description for TaskEvent<%s>", self.pk
            )
        return html

    def _get_status_change_html(self):
        prev_status = self.data.get("prev_status")
        prev_status = TaskStatus[prev_status].label

        next_status = self.data.get("next_status")
        next_status = TaskStatus[next_status].label

        return (
            self._get_user_anchor_tag(self.user)
            + f"changed status from <strong>{prev_status}</strong> "
            + f"to <strong>{next_status}</strong>"
        )

    def _get_suspend_html(self):
        prev_user_id = self.data.get("prev_user_id")
        prev_user = User.objects.get(id=prev_user_id)

        return (
            "This task was suspended because "
            + self._get_user_anchor_tag(prev_user)
            + " was removed from the case"
        )

    def _get_reassign_html(self):
        prev_user_id = self.data.get("prev_user_id")
        prev_user = User.objects.get(id=prev_user_id)

        next_user_id = self.data.get("next_user_id")
        next_user = User.objects.get(id=next_user_id)

        return (
            "This task was reassigned from "
            + self._get_user_anchor_tag(prev_user)
            + " to "
            + self._get_user_anchor_tag(next_user)
            + " because the case user was changed"
        )

    def _get_resume_html(self):
        next_user_id = self.data.get("next_user_id")
        next_user = User.objects.get(id=next_user_id)

        return (
            "This task was resumed because "
            + self._get_user_anchor_tag(next_user)
            + " was added to the case"
        )

    def _get_user_anchor_tag(self, user: User):
        user_url = reverse("account-detail", args=(user.pk,))
        return f'<a href="{user_url}">{user.first_name}</a>'

    @staticmethod
    def create_status_change(
        task: Task,
        user: User,
        prev_status: str,
        next_status: str,
        note: str | None = None,
    ):
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

    @staticmethod
    def create_suspend(task: Task, prev_user: User):
        return TaskEvent.objects.create(
            type=TaskEventType.SUSPEND,
            task=task,
            data={
                "prev_user_id": prev_user.pk,
            },
        )

    @staticmethod
    def create_reassign(task: Task, prev_user: User, next_user: User):
        return TaskEvent.objects.create(
            type=TaskEventType.REASSIGN,
            task=task,
            data={
                "prev_user_id": prev_user.pk,
                "next_user_id": next_user.pk,
            },
        )

    @staticmethod
    def create_resume(task: Task, next_user: User):
        return TaskEvent.objects.create(
            type=TaskEventType.RESUME,
            task=task,
            data={
                "next_user_id": next_user.pk,
            },
        )