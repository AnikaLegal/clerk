from rest_framework import serializers
from django.urls import reverse

from case.serializers import IssueSerializer, UserSerializer
from case.serializers.fields import LocalDateField
from .models import Task, TaskComment


class TaskListIssueSerializer(IssueSerializer):
    class Meta:
        model = IssueSerializer.Meta.model
        fields = (
            "id",
            "fileref",
            "topic",
            "url",
        )

    # Bypass the parent method as it references a field we do not include.
    def get_fields(self, *args, **kwargs):
        return super(IssueSerializer, self).get_fields(*args, **kwargs)


class TaskListUserSerializer(UserSerializer):
    class Meta:
        model = UserSerializer.Meta.model
        read_only_fields = UserSerializer.Meta.read_only_fields
        fields = (
            "id",
            "full_name",
            "url",
        )


class TaskListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = (
            "id",
            "type",
            "name",
            "status",
            "issue",
            "owner",
            "assigned_to",
            "is_open",
            "is_suspended",
            "created_at",
            "closed_at",
            "days_open",
            "url",
        )
        read_only_fields = (
            "is_open",
            "is_suspended",
        )

    issue = TaskListIssueSerializer(read_only=True)
    owner = TaskListUserSerializer(read_only=True)
    assigned_to = TaskListUserSerializer(read_only=True)
    created_at = LocalDateField(read_only=True)
    closed_at = LocalDateField(read_only=True)
    days_open = serializers.IntegerField(read_only=True)
    url = serializers.SerializerMethodField(read_only=True)

    def get_url(self, obj):
        return reverse("task-detail", args=(obj.pk,))


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = (
            "id",
            "type",
            "name",
            "description",
            "status",
            "issue_id",
            "issue",
            "owner_id",
            "owner",
            "assigned_to_id",
            "assigned_to",
            "is_open",
            "is_suspended",
            "created_at",
            "closed_at",
            "days_open",
            "url",
        )
        read_only_fields = (
            "is_open",
            "is_suspended",
        )

    issue_id = serializers.UUIDField(write_only=True)
    issue = IssueSerializer(read_only=True)
    owner_id = serializers.IntegerField(write_only=True)
    owner = UserSerializer(read_only=True)
    assigned_to_id = serializers.IntegerField(write_only=True)
    assigned_to = UserSerializer(read_only=True)

    created_at = LocalDateField(read_only=True)
    closed_at = LocalDateField(read_only=True)
    days_open = serializers.IntegerField(read_only=True)


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
            "issue__topic",
            "q",
            "my_tasks",
        )
        extra_kwargs = {f: {"required": False} for f in fields}

    issue__topic = serializers.CharField(required=False)
    # Special case searches.
    q = serializers.CharField(required=False)  # General query.
    my_tasks = serializers.BooleanField(required=False)


class TaskCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskComment
        fields = (
            "id",
            "task_id",
            "creator_id",
            "creator",
            "created_at",
            "type",
            "text",
        )

    task_id = serializers.IntegerField()
    creator_id = serializers.IntegerField(write_only=True)
    creator = TaskListUserSerializer(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
