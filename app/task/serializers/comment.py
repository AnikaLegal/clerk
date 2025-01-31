from rest_framework import serializers
from task.models import TaskComment

from .task import TaskListUserSerializer


class TaskCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskComment
        fields = (
            "id",
            "task_id",
            "creator_id",
            "creator",
            "created_at",
            "text",
        )

    task_id = serializers.IntegerField()
    creator_id = serializers.IntegerField(write_only=True)
    creator = TaskListUserSerializer(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)