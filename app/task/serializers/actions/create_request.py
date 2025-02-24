from rest_framework import serializers
from task.models import Task
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
