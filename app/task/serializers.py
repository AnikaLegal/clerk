from rest_framework import serializers
from rest_framework_serializer_extensions.serializers import SerializerExtensionsMixin
from django.urls import reverse

from case.serializers import IssueSerializer, UserSerializer
from .models import Task


class IssueExtSerializer(SerializerExtensionsMixin, IssueSerializer):
    class Meta:
        model = IssueSerializer.Meta.model
        fields = IssueSerializer.Meta.fields


class UserExtSerializer(SerializerExtensionsMixin, UserSerializer):
    class Meta:
        model = UserSerializer.Meta.model
        fields = UserSerializer.Meta.fields
        read_only_fields = UserSerializer.Meta.read_only_fields


class TaskSerializer(SerializerExtensionsMixin, serializers.ModelSerializer):
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
            "created_at",
            "closed_at",
            "days_open",
            "url",
        )
        read_only_fields = (
            "is_open",
            "is_suspended",
            "created_at",
            "closed_at",
        )
        expandable_fields = dict(
            issue=IssueExtSerializer,
            owner=UserExtSerializer,
            assigned_to=UserExtSerializer,
        )

    days_open = serializers.IntegerField(read_only=True)
    url = serializers.SerializerMethodField(read_only=True)

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

    q = serializers.CharField(required=False)  # General query.
    issue__topic = serializers.CharField(required=False)
