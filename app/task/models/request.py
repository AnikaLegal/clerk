from accounts.models import User
from auditlog.registry import auditlog
from core.models import TimestampedModel
from django.db import models, transaction


class TaskRequestType(models.TextChoices):
    APPROVAL = "APPROVAL", "Approval request"


class TaskRequestStatus(models.TextChoices):
    PENDING = "PENDING"
    DONE = "DONE"


class TaskRequest(TimestampedModel):
    class Meta:
        verbose_name = "request"

    type = models.TextField(choices=TaskRequestType.choices)
    status = models.TextField(
        choices=TaskRequestStatus.choices, default=TaskRequestStatus.PENDING
    )
    is_approved = models.BooleanField(default=False)

    from_task = models.ForeignKey(
        "task.Task",
        on_delete=models.CASCADE,
        related_name="requests",
    )
    from_user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="+",
    )
    from_comment = models.TextField()

    to_task = models.OneToOneField(
        "task.Task",
        on_delete=models.CASCADE,
        related_name="request",
    )
    to_user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="+",
    )
    to_comment = models.TextField(blank=True, null=True)

    @transaction.atomic
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


auditlog.register(
    TaskRequest,
    exclude_fields=["created_at", "modified_at"],
    serialize_data=True,
)
