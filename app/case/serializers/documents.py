import os

from core.models import CaseSubtopic, CaseTopic
from django.utils import timezone
from django.utils.text import slugify
from rest_framework import serializers
from microsoft.service import upload_file


class ISO8601StringDateField(serializers.DateField):
    def to_representation(self, value):
        value = timezone.localtime(timezone.datetime.fromisoformat(value)).date()
        return super().to_representation(value)


class DocumentTemplateFilterSerializer(serializers.Serializer):
    topic = serializers.ChoiceField(choices=CaseTopic.ACTIVE_CHOICES, required=True)
    subtopic = serializers.ChoiceField(choices=CaseSubtopic.choices, required=False)
    name = serializers.CharField(required=False)


class DocumentTemplateSerializer(serializers.Serializer):
    id = serializers.CharField(required=True)
    name = serializers.CharField(required=True)
    url = serializers.CharField(source="webUrl", required=True)
    created_at = ISO8601StringDateField(source="createdDateTime")
    modified_at = ISO8601StringDateField(source="lastModifiedDateTime")


class DocumentTemplateFileSerializer(serializers.Serializer):
    topic = serializers.ChoiceField(choices=CaseTopic.ACTIVE_CHOICES, required=True)
    subtopic = serializers.ChoiceField(choices=CaseSubtopic.choices, required=False)
    files = serializers.ListField(child=serializers.FileField(), allow_empty=False)

    def create(self, validated_data):
        topic = validated_data.get("topic")
        subtopic = validated_data.get("subtopic", "")
        path = os.path.join("templates", slugify(topic), slugify(subtopic)).rstrip("/")

        for file in validated_data["files"]:
            upload_file(path, file)
        return True
