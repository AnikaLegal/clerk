from rest_framework import serializers
from django.urls import reverse

from .models import Task
from .models.template import TaskType
from .models.task import TaskStatus
from case.serializers.fields import TextChoiceField


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = (
            "id",
            "type",
            "name",
            "description",
            "status",
            "is_open",
            "is_suspended",
            "issue_id",
            "owner_id",
            "assigned_to_id",
            "url",
        )

    type = TextChoiceField(TaskType)
    status = TextChoiceField(TaskStatus)
    issue_id = serializers.UUIDField()
    owner_id = serializers.IntegerField()
    assigned_to_id = serializers.IntegerField()

    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        return reverse("task-detail", args=(obj.pk,))


class TaskSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = (
            "type",
            "name",
            "status",
            "is_open",
            "is_suspended",
            "issue",
            "owner",
            "assigned_to",
        )
        extra_kwargs = {f: {"required": False} for f in fields}
