import os

from core.models.document_template import DocumentTemplate
from core.models import CaseSubtopic, CaseTopic
from core.models.issue import EvictionSubtopic
from rest_framework import serializers


class DocumentTemplateFilterSerializer(serializers.Serializer):
    topic = serializers.ChoiceField(choices=CaseTopic.ACTIVE_CHOICES, required=False)
    subtopic = serializers.ChoiceField(choices=CaseSubtopic.choices, required=False)
    name = serializers.CharField(required=False)


class DocumentTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentTemplate
        fields = [
            "id",
            "topic",
            "subtopic",
            "name",
            "url",
            "created_at",
            "modified_at",
            "files",
        ]

    # read only fields
    id = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    url = serializers.CharField(source="file.url", read_only=True)
    created_at = serializers.DateTimeField(read_only=True, format="%d/%m/%Y")
    modified_at = serializers.DateTimeField(read_only=True, format="%d/%m/%Y")

    # read/write fields
    topic = serializers.ChoiceField(choices=CaseTopic.ACTIVE_CHOICES, required=True)
    subtopic = serializers.ChoiceField(choices=CaseSubtopic.choices, required=False)

    # write only fields
    files = serializers.ListField(
        child=serializers.FileField(), allow_empty=False, write_only=True
    )

    def validate(self, attrs):
        topic = attrs.get("topic")
        subtopic = attrs.get("subtopic", "")

        if topic == CaseTopic.EVICTION and subtopic not in EvictionSubtopic:
            error_message = f"When topic is {topic}, subtopic must be one of: "
            raise serializers.ValidationError(
                {"subtopic": error_message + ", ".join(EvictionSubtopic)}
            )

        return attrs

    def create(self, validated_data):
        files = validated_data.pop("files")
        topic = validated_data.get("topic")
        subtopic = validated_data.get("subtopic", "")

        for file in files:
            DocumentTemplate.objects.create(
                topic=topic,
                subtopic=subtopic,
                file=file,
            )
        return validated_data
