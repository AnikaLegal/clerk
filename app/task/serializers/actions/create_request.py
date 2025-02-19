from django.db import transaction
from rest_framework import serializers
from task.models import Task, TaskEvent
from task.models.task import RequestTaskType


class TaskCreateRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = (
            "id",
            "type",
            "name",
            "description",
            "assigned_to_id",
            "issue_id",
            "requesting_task_id",
        )

    type = serializers.ChoiceField(choices=RequestTaskType.choices)
    assigned_to_id = serializers.IntegerField(required=True)
    issue_id = serializers.UUIDField(write_only=True)
    requesting_task_id = serializers.IntegerField(write_only=True)

    @transaction.atomic
    def create(self, validated_data):
        instance: Task = super().create(validated_data)
        self.create_event(instance)
        return instance

    def validate(self, attrs):
        return attrs

    def create_event(self, task):
        request = self.context.get("request", None)
        if request:
            TaskEvent.create_request(
                task=task.requesting_task,
                user=request.user,
                request_task=task,
                note=task.description,
            )
