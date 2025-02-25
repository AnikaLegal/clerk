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
