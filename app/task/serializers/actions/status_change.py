from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from task.models import Task
from task.models.task import TaskStatus


class TaskStatusChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = (
            "id",
            "status",
        )

    def update(self, instance, validated_data):
        request = self.context.get("request", None)
        if request and not request.user.is_paralegal_or_better:
            raise PermissionDenied()
        instance = super().update(instance, validated_data)
        return instance

    def validate_status(self, value):
        # Only lawyers can finish a task when approval is required but not yet
        # given.
        request = self.context.get("request", None)
        if request and not request.user.is_lawyer:
            instance: Task | None = self.instance
            if not instance or (
                value in [TaskStatus.DONE, TaskStatus.NOT_DONE]
                and instance.is_approval_required
                and not instance.is_approved
            ):
                raise PermissionDenied(detail="Approval is required")
        return value
