import logging

from accounts.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone

from .activity import TaskActivity
from .task import Task, TaskStatus, RequestTaskType

logger = logging.getLogger(__name__)


class TaskEventType(models.TextChoices):
    """
    The type of the event.
    """

    REASSIGN = "REASSIGN"
    REQUEST = "REQUEST"
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

    #
    # TODO: Perhaps tidy this by moving event creation & generating HTML from
    # the model to separate functions elsewhere?
    #
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
            elif self.type == TaskEventType.REQUEST:
                html = self._get_request_html()
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
            _get_user_anchor_tag(self.user)
            + f" changed the status from <strong>{prev_status}</strong>"
            + f" to <strong>{next_status}</strong>."
        )

    def _get_suspend_html(self):
        prev_user_id = self.data.get("prev_user_id")
        prev_user = User.objects.get(id=prev_user_id)

        return (
            "This task was suspended because "
            + _get_user_anchor_tag(prev_user)
            + " was removed from the case."
        )

    def _get_reassign_html(self):
        prev_user_id = self.data.get("prev_user_id")
        prev_user = User.objects.get(id=prev_user_id)

        next_user_id = self.data.get("next_user_id")
        next_user = User.objects.get(id=next_user_id)

        return (
            "This task was reassigned from "
            + _get_user_anchor_tag(prev_user)
            + " to "
            + _get_user_anchor_tag(next_user)
            + " because the case user was changed."
        )

    def _get_resume_html(self):
        next_user_id = self.data.get("next_user_id")
        next_user = User.objects.get(id=next_user_id)

        return (
            "This task was resumed because "
            + _get_user_anchor_tag(next_user)
            + " was added to the case."
        )

    def _get_request_html(self):
        request_task_id = self.data.get("request_task_id")
        request_task = Task.objects.get(id=request_task_id)

        if request_task.type == RequestTaskType.APPROVAL:
            return (
                _get_user_anchor_tag(self.user)
                + " submitted an "
                + f'<a href="{request_task.url}">approval request</a>'
                + " for this task."
            )

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

    @staticmethod
    def create_request(task: Task, user: User, request_task: Task):
        return TaskEvent.objects.create(
            type=TaskEventType.REQUEST,
            task=task,
            user=user,
            data={
                "request_task_id": request_task.pk,
            },
        )


def _get_user_anchor_tag(user: User):
    user_url = reverse("account-detail", args=(user.pk,))
    return f'<a href="{user_url}">{user.first_name}</a>'
