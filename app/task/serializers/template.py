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

    def to_internal_value(self, data):
        # Convert empty strings to null for some fields. This is just a
        # convenience so we don't have to do it on the frontend.
        for field in ("due_in",):
            if field in data and data[field] == "":
                data[field] = None
        return super().to_internal_value(data)
