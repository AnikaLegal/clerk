from rest_framework import serializers
from task.models import TaskActivity, TaskComment, TaskEvent

from .comment import TaskCommentSerializer
from .event import TaskEventSerializer


class TaskActivitySerializer(serializers.ModelSerializer):
    class GenericObjectRelatedField(serializers.RelatedField):
        def to_representation(self, value):
            if isinstance(value, TaskComment):
                serializer = TaskCommentSerializer(value)
            elif isinstance(value, TaskEvent):
                serializer = TaskEventSerializer(value)
            else:
                raise Exception("Unexpected type of data object")
            return serializer.data

    type = serializers.SerializerMethodField(read_only=True)
    data = GenericObjectRelatedField(source="content_object", read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    modified_at = serializers.DateTimeField(read_only=True)

    def get_type(self, obj):
        return obj.content_type.name

    class Meta:
        model = TaskActivity
        fields = (
            "id",
            "task_id",
            "type",
            "data",
            "created_at",
            "modified_at",
        )
