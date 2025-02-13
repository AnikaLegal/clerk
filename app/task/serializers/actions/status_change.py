from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from task.models import Task, TaskEvent
from task.models.task import TaskStatus


class TaskStatusChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = (
            "id",
            "status",
            "comment",
        )

    # NOTE: This field is not part of the Task model.
    comment = serializers.CharField(required=False, write_only=True)

    @transaction.atomic
    def update(self, instance, validated_data):
        status = validated_data.get("status")
        # NOTE: Remove the comment field as it's not part of the Task model.
        comment = validated_data.pop("comment", None)
        self.create_event(instance, status, comment)

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
        # Only lawyers+ can finish a task when approval is required but not yet
        # given.
        if value in [TaskStatus.DONE, TaskStatus.NOT_DONE]:
            request = self.context.get("request", None)
            if request and not request.user.is_lawyer_or_better:
                instance: Task | None = self.instance
                if (
                    instance
                    and instance.is_approval_required
                    and not instance.is_approved
                ):
                    raise PermissionDenied(detail="Approval is required")
        return value

    def create_event(self, instance, status, comment):
        request = self.context.get("request", None)
        if request:
            TaskEvent.create_status_change(
                task=instance,
                user=request.user,
                prev_status=instance.status,
                next_status=status,
                note=comment,
            )
