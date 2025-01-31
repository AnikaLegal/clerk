from rest_framework import serializers
from task.models import TaskActivity, TaskComment
from .comment import TaskCommentSerializer


class TaskActivitySerializer(serializers.ModelSerializer):
    class GenericObjectRelatedField(serializers.RelatedField):
        def to_representation(self, value):
            if isinstance(value, TaskComment):
                serializer = TaskCommentSerializer(value)
            else:
                raise Exception("Unexpected type of tagged object")
            return serializer.data

    created_at = serializers.DateTimeField(read_only=True)
    data = GenericObjectRelatedField(source="content_object", read_only=True)
    type = serializers.SerializerMethodField(read_only=True)

    def get_type(self, obj):
        return obj.content_type.name

    class Meta:
        model = TaskActivity
        fields = (
            "id",
            "task_id",
            "created_at",
            "data",
            "type",
        )

