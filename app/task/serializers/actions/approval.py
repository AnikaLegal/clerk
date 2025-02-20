from django.db import transaction
from rest_framework import serializers
from task.models import Task, TaskEvent


class TaskApprovalRequestingTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = (
            "id",
            "is_approved",
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

        requesting_task = instance.requesting_task
        for attr, value in data.items():
            setattr(requesting_task, attr, value)
        requesting_task.save()

        self.create_event(instance, data, comment)
        self.create_event(requesting_task, data, comment)

        return super().update(instance, validated_data)

    def create_event(self, instance, data, comment):
        request = self.context.get("request", None)
        if request:
            TaskEvent.create_approval(
                task=instance,
                user=request.user,
                data=data,
                note=comment,
            )
