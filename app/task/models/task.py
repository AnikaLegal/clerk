from accounts.models import User
from auditlog.registry import auditlog
from core.models import Issue, TimestampedModel
from django.db import models
from django.db.models import functions
from django.urls import reverse
from django.utils import timezone
from task.auditlog import LogDataMixin

from .group import TaskGroup
from .template import TaskTemplate, TaskTemplateType
from .trigger import TasksCaseRole


class RequestTaskType(models.TextChoices):
    """
    The possible types of request tasks.
    """

    QUESTION = "QUESTION", "Question"
    APPROVAL = "APPROVAL", "Approval request"


TaskType = list(TaskTemplateType.choices) + list(RequestTaskType.choices)


class TaskStatus(models.TextChoices):
    """
    The status of the task.
    """

    NOT_STARTED = "NOT_STARTED", "Not started"
    IN_PROGRESS = "IN_PROGRESS", "In progress"
    DONE = "DONE", "Done"
    NOT_DONE = "NOT_DONE", "Not done"


class Task(TimestampedModel, LogDataMixin):
    type = models.CharField(max_length=32, choices=TaskType)
    name = models.TextField()
    description = models.TextField(blank=True, default="")
    status = models.CharField(
        max_length=32, choices=TaskStatus.choices, default=TaskStatus.NOT_STARTED
    )
    due_at = models.DateField(blank=True, null=True, default=None)
    closed_at = models.DateTimeField(blank=True, null=True, default=None)
    is_urgent = models.BooleanField(default=False)

    # Fields related to approval requests
    is_approval_required = models.BooleanField(default=False)
    is_approval_pending = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)

    requesting_task = models.ForeignKey(
        "self", on_delete=models.CASCADE, blank=True, null=True, related_name="requests"
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

    # The user the task is assigned to.
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="+",
    )
    # The role of the user the task is assigned to.
    # TODO: explain some more.
    assignee_role = models.CharField(
        max_length=32,
        choices=TasksCaseRole.choices,
        default=None,
        blank=True,
        null=True,
    )

    # If the task was created by the system then this refers to the template
    # used to create the task.
    template = models.ForeignKey(
        TaskTemplate, on_delete=models.SET_NULL, blank=True, null=True
    )

    group = models.ForeignKey(
        TaskGroup, on_delete=models.SET_NULL, blank=True, null=True
    )
    group_order = models.IntegerField(default=-1)

    @property
    def url(self):
        if self.pk:
            return reverse("task-detail", args=(self.pk,))

    def save(self, *args, **kwargs):
        # Set internal status flag to indicate if a notification is potentially
        # required.
        try:
            prev_task = Task.objects.get(pk=self.pk)
        except Task.DoesNotExist:
            prev_task = None
        self.is_notify_pending = self.assigned_to is not None and (
            prev_task is None or prev_task.assigned_to != self.assigned_to
        )

        # Set some internal status flags.
        self.is_open = self.status not in [TaskStatus.DONE, TaskStatus.NOT_DONE]
        self.is_suspended = not self.assigned_to

        # Set the closed date when the task is first closed and clear the closed
        # date if the task is reopened.
        if self.is_open:
            if self.closed_at is not None:
                self.closed_at = None
        else:
            if self.closed_at is None:
                self.closed_at = timezone.now()

        super().save(*args, **kwargs)

    @staticmethod
    def annotate_with_days_open(
        queryset: models.QuerySet["Task"],
    ) -> models.QuerySet["Task"]:
        expression = models.Case(
            models.When(
                models.Q(closed_at__isnull=False),
                then=(models.F("closed_at") - models.F("created_at")),
            ),
            default=(functions.Now() - models.F("created_at")),
            output_field=models.DurationField(),
        )
        return queryset.annotate(days_open=(functions.ExtractDay(expression)))


auditlog.register(
    Task,
    exclude_fields=["created_at", "modified_at"],
    serialize_data=True,
)
