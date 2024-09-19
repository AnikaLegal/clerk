from core.models import Service
from rest_framework import serializers


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = (
            "id",
            "issue_id",
            "category",
            "type",
            "started_at",
            "finished_at",
            "notes",
        )

    issue_id = serializers.UUIDField()
