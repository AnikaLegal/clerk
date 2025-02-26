from django.db import transaction
from rest_framework import serializers
from task.models import Task


class TaskApprovalRequestingTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = (
            "id",
            "is_approved",
            "is_approval_pending",
            "comment",
        )

    # NOTE: This field is not part of the Task model.
    comment = serializers.CharField(required=False, write_only=True)


class TaskApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = (
            "id",
            "status",
            "requesting_task",
        )

    requesting_task = TaskApprovalRequestingTaskSerializer(write_only=True)

    @transaction.atomic
    def update(self, instance, validated_data):
        data = validated_data.pop("requesting_task", None)

        # NOTE: Remove the comment field as it's not part of the Task model.
        comment = data.pop("comment", None)

        # Update the requesting task.
        requesting_task = instance.requesting_task
        try:
            # NOTE: Associate some data with this instance so we can access it
            # later when we process the log entry for the update.
            requesting_task.set_log_data("request_task_id", instance.id)
            requesting_task.set_log_data("comment", comment)

            for attr, value in data.items():
                setattr(requesting_task, attr, value)

            requesting_task.save()
        finally:
            requesting_task.clear_log_data()

        return super().update(instance, validated_data)

    def validate_requesting_task(self, requesting_task):
        is_approval_pending = requesting_task.get("is_approval_pending", None)
        is_approved = requesting_task.get("is_approved", None)
        comment = requesting_task.get("comment", None)

        # Require a comment for declined approval requests.
        if is_approval_pending is False and is_approved is False and not comment:
            raise serializers.ValidationError(
                {"comment": "A comment is required for declined approval requests"}
            )
        return requesting_task
