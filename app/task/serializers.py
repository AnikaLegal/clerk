from rest_framework import serializers
from django.urls import reverse

from .models import Task
from .models.template import TaskType
from .models.task import TaskStatus
from case.serializers.fields import TextChoiceField
from case.serializers.issue import IssueSerializer
from case.serializers.user import UserSerializer


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
            "issue",
            "owner_id",
            "owner",
            "assigned_to_id",
            "assigned_to",
            "url",
        )

    type = TextChoiceField(TaskType)
    status = TextChoiceField(TaskStatus)

    issue_id = serializers.UUIDField()
    issue = IssueSerializer(read_only=True)
    owner_id = serializers.IntegerField()
    owner = UserSerializer(read_only=True)
    assigned_to_id = serializers.IntegerField()
    assigned_to = UserSerializer(read_only=True)

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
            "q",
            "issue__topic",
        )
        extra_kwargs = {f: {"required": False} for f in fields}

    # General query.
    q = serializers.CharField(required=False)
    issue__topic = serializers.CharField(required=False)
