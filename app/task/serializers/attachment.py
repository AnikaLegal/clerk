from rest_framework import serializers
from task.models import TaskAttachment


class TaskAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskAttachment
        fields = (
            "id",
            "task_id",
            "comment_id",
            "content_type",
            "file",
            "name",
            "url",
            "created_at",
            "modified_at",
        )

    task_id = serializers.IntegerField()
    comment_id = serializers.IntegerField(allow_null=True)
    content_type = serializers.CharField(read_only=True)
    file = serializers.FileField(write_only=True)
    name = serializers.CharField(source="file.name", read_only=True)
    url = serializers.URLField(source="file.url", read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    modified_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        file = validated_data["file"]
        data = {
            **validated_data,
            "content_type": file.content_type,
        }
        return super().create(data)
