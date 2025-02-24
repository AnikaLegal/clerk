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

    # NOTE: This field is not part of the Task model.
    comment = serializers.CharField(required=False, write_only=True)

    @transaction.atomic
    def update(self, instance, validated_data):
        # NOTE: Also remove the comment field as it's not part of the Task model.
        comment = validated_data.pop("comment", None)

        # NOTE: Associate some data with this instance so we can access it later
        # when we process the log entry for the status change.
        instance.set_log_data("comment", comment)
        try:
            return super().update(instance, validated_data)
        finally:
            instance.clear_log_data()

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
