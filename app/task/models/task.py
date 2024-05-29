from django.db import models

from accounts.models import User
from core.models import TimestampedModel, Issue
from .template import TaskTemplate, TaskType
from .comment import TaskComment, CommentType
from .attachment import TaskAttachment


class TaskStatus(models.TextChoices):
    """
    The status of the task.
    """

    NOT_STARTED = "NOT_STARTED", "Not started"
    IN_PROGRESS = "IN_PROGRESS", "In progress"
    DONE = "DONE", "Done"
    NOT_DONE = "NOT_DONE", "Not done"


class OwnerRole(models.TextChoices):
    """
    Used to keep track of the previous ownership role of tasks when their owner
    is removed from a case.
    """

    PARALEGAL = "PARALEGAL", "Paralegal"
    LAWYER = "LAWYER", "Lawyer"


class Task(TimestampedModel):

    type = models.CharField(max_length=32, choices=TaskType.choices)
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True, default="")
    status = models.CharField(
        max_length=32, choices=TaskStatus.choices, default=TaskStatus.NOT_STARTED
    )

    # Internal status fields used for convenience.
    is_open = models.BooleanField(default=True)
    is_suspended = models.BooleanField(default=False)

    # We use these two flags to handle sending notifications when the assignee
    # changes. The flags operate as follows:
    #
    # - is_notify_pending: indicates that the assignee has changed and,
    #   therefore, we potentially need to notify them.
    #
    # - is_system_update: indicates that the system is creating or updating
    # tasks, potentially en masse (e.g. creating multiple tasks for a single
    # user in response to a task trigger being activated) and will only send out
    # a single notification instead of one for every created or updated task.
    #
    is_notify_pending = models.BooleanField(default=False)
    is_system_update = models.BooleanField(default=False)

    # The issue to which the task relates.
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)

    # The original assignee.
    owner = models.ForeignKey(
        User, on_delete=models.PROTECT, blank=True, null=True, related_name="+"
    )
    # Internal field used to handle task ownership & assignment when users are
    # removed from & assigned back to a case. TODO: explain.
    prev_owner_role = models.CharField(
        max_length=32, choices=OwnerRole.choices, default=None, blank=True, null=True
    )

    # The current assignee.
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="+",
    )

    # If the task was created by the system then this refers to the template
    # used to create the task.
    template = models.ForeignKey(
        TaskTemplate, on_delete=models.PROTECT, blank=True, null=True
    )

    def save(self, *args, **kwargs):
        # As a convenience, set the owner as the assignee if the task does not
        # have one.
        if self.owner and not self.assigned_to:
            self.assigned_to = self.owner

        # Set internal status flag to indicate if a notification is potentially
        # required.
        try:
            prev_task = Task.objects.get(pk=self.pk)
        except Task.DoesNotExist:
            prev_task = None
        self.is_notify_pending = self.assigned_to_id is not None and (
            prev_task is None or prev_task.assigned_to_id != self.assigned_to_id
        )

        # Set some internal status flags.
        self.is_open = self.status not in [TaskStatus.DONE, TaskStatus.NOT_DONE]
        self.is_suspended = not self.owner and self.prev_owner_role is not None

        super().save(*args, **kwargs)

    # Convenience method used to add a comment related to the task instance.
    def add_comment(
        self, text: str, type: CommentType = CommentType.SYSTEM
    ) -> TaskComment:
        return TaskComment.objects.create(
            task=self,
            type=type,
            text=text,
        )

    # Convenience method used to add an attachment related to the task instance.
    def add_attachment(
        self, file: str, comment: TaskComment | None = None
    ) -> TaskAttachment:
        return TaskAttachment.objects.create(
            task=self,
            comment=comment,
            file=file,
        )
