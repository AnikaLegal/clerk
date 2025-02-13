from django.db import transaction
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
            "issue_id",
            "assigned_to_id",
            "request_task_id",
        )

    type = serializers.ChoiceField(choices=RequestTaskType.choices)
    issue_id = serializers.UUIDField()
    assigned_to_id = serializers.IntegerField()
    request_task_id = serializers.IntegerField()

    @transaction.atomic
    def create(self, validated_data):
        self.create_event()
        return super().create(validated_data)

    def validate(self, attrs):
        return attrs

    def create_event(self):
        request = self.context.get("request", None)
        if request:
            pass
