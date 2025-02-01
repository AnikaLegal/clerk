from rest_framework import serializers
from task.models import TaskEvent

from .task import TaskListUserSerializer


class TaskEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskEvent
        fields = (
            "id",
            "type",
            "task_id",
            "user",
            "created_at",
            "html",
            "note",
        )

    task_id = serializers.IntegerField()
    user = TaskListUserSerializer(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    html = serializers.SerializerMethodField(read_only=True)

    def get_html(self, obj):
        return obj.get_html()