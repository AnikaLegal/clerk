import logging

from accounts.models import User
from core.models import Issue
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone

from .activity import TaskActivity
from .task import RequestTaskType, Task, TaskStatus

logger = logging.getLogger(__name__)


class TaskEventType(models.TextChoices):
    """
    The type of the event.
    """

    APPROVAL_REQUEST = "APPROVAL_REQUEST", "Approval Request"
    APPROVAL_RESPONSE = "APPROVAL_RESPONSE", "Approval Response"
    CANCEL = "CANCEL", "Task Cancelled"
    REASSIGN = "REASSIGN", "Task Reassigned"
    RESUME = "RESUME", "Task Resumed"
    STATUS_CHANGE = "STATUS_CHANGE", "Status Change"
    SUSPEND = "SUSPEND", "Task Suspended"


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
    data = models.JSONField(null=True)
    note_html = models.TextField(null=True)
    created_at = models.DateTimeField(default=timezone.now)

    @transaction.atomic
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        TaskActivity.objects.create(content_object=self)

    #
    # TODO: Perhaps tidy this by moving generating HTML from the model to
    # separate functions elsewhere?
    #
    def get_desc_html(self):
        html = ""
        try:
            if self.type == TaskEventType.APPROVAL_RESPONSE:
                html = self._get_approval_html()
            elif self.type == TaskEventType.CANCEL:
                html = self._get_cancelled_html()
            elif self.type == TaskEventType.STATUS_CHANGE:
                html = self._get_status_change_html()
            elif self.type == TaskEventType.SUSPEND:
                html = self._get_suspend_html()
            elif self.type == TaskEventType.REASSIGN:
                html = self._get_reassign_html()
            elif self.type == TaskEventType.RESUME:
                html = self._get_resume_html()
            elif self.type == TaskEventType.APPROVAL_REQUEST:
                html = self._get_approval_request_html()
        except Exception:
            logger.exception(
                "Could not generate description for TaskEvent<%s>", self.pk
            )
        return html

    def _get_approval_html(self):
        is_approved = self.data.get("is_approved")

        user_a_tag = _get_user_a_tag(self.user)
        determiner = "the" if self.task.type == RequestTaskType.APPROVAL else "this"
        if is_approved:
            return f"{user_a_tag} <strong>approved</strong> the request to complete {determiner} task."
        return f"{user_a_tag} suggested that the following changes are necessary to complete {determiner} task."

    def _get_cancelled_html(self):
        issue: Issue = self.task.issue
        return (
            "This task was cancelled because case "
            + f'<a href="{issue.url}">{issue.fileref}</a>'
            + " was closed."
        )

    def _get_status_change_html(self):
        prev_status = self.data.get("prev_status")
        prev_status = TaskStatus[prev_status].label

        next_status = self.data.get("next_status")
        next_status = TaskStatus[next_status].label

        return (
            _get_user_a_tag(self.user)
            + f" changed the status from <strong>{prev_status}</strong>"
            + f" to <strong>{next_status}</strong>."
        )

    def _get_suspend_html(self):
        prev_user_id = self.data.get("prev_user_id")
        prev_user = User.objects.get(id=prev_user_id)

        return (
            "This task was suspended because "
            + _get_user_a_tag(prev_user)
            + " was removed from the case."
        )

    def _get_reassign_html(self):
        prev_user_id = self.data.get("prev_user_id")
        prev_user = User.objects.get(id=prev_user_id)

        next_user_id = self.data.get("next_user_id")
        next_user = User.objects.get(id=next_user_id)

        return (
            "This task was reassigned from "
            + _get_user_a_tag(prev_user)
            + " to "
            + _get_user_a_tag(next_user)
            + " because the case user was changed."
        )

    def _get_resume_html(self):
        next_user_id = self.data.get("next_user_id")
        next_user = User.objects.get(id=next_user_id)

        return (
            "This task was resumed because "
            + _get_user_a_tag(next_user)
            + " was added to the case."
        )

    def _get_approval_request_html(self):
        request_task_id = self.data.get("request_task_id")
        request_task = Task.objects.get(id=request_task_id)

        return (
            _get_user_a_tag(self.user)
            + " submitted an "
            + f'<a href="{request_task.url}">approval request</a>'
            + " for this task."
        )


def _get_user_a_tag(user: User):
    user_url = reverse("account-detail", args=(user.pk,))
    return f'<a href="{user_url}">{user.first_name}</a>'
