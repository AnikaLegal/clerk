from rest_framework import serializers
from task.models.event import TaskEvent, TaskEventType

from .task import TaskListUserSerializer


class TaskEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskEvent
        fields = (
            "id",
            "type",
            "type_display",
            "task_id",
            "user",
            "desc_html",
            "note_html",
            "created_at",
            "modified_at",
        )
        read_only_fields = fields

    type = serializers.ChoiceField(choices=TaskEventType.choices)
    type_display = serializers.CharField(source="get_type_display")
    task_id = serializers.IntegerField()
    user = TaskListUserSerializer()
    desc_html = serializers.CharField(source="get_desc_html")
    created_at = serializers.DateTimeField()
    modified_at = serializers.DateTimeField()
