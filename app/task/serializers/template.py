from rest_framework import serializers
from task.models import TaskTemplate


class TaskTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskTemplate
        fields = (
            "id",
            "type",
            "name",
            "description",
            "due_in",
            "is_urgent",
            "is_approval_required",
        )

    id = serializers.IntegerField(required=False)
