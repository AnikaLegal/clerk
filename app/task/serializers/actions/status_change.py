from django.db import transaction
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
            "comment",
        )

    comment = serializers.CharField(required=False)

    @transaction.atomic
    def update(self, instance: Task, validated_data):
        comment = validated_data.pop("comment", None)
        if comment:
            # TODO: create event.
            pass
        return super().update(instance, validated_data)

    def validate(self, attrs):
        # Require explanatory comment if the task is not done.
        status = attrs.get("status")
        comment = attrs.get("comment")
        if status == TaskStatus.NOT_DONE and not comment:
            raise serializers.ValidationError(
                {"comment": self.fields["comment"].error_messages["required"]}
            )
        return attrs

    def validate_status(self, value):
        # Only lawyers can finish a task when approval is required but not yet
        # given.
        request = self.context.get("request", None)
        if request and not request.user.is_lawyer:
            instance: Task | None = self.instance
            if (
                instance
                and instance.is_approval_required
                and not instance.is_approved
                and value in [TaskStatus.DONE, TaskStatus.NOT_DONE]
            ):
                raise PermissionDenied(detail="Approval is required")
        return value
