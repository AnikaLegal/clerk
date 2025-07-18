from core.models import CaseTopic
from core.models.document_template import DocumentTemplate
from django.utils import timezone
from rest_framework import serializers


class DocumentTemplateFilterSerializer(serializers.Serializer):
    topic = serializers.ChoiceField(choices=CaseTopic.ACTIVE_CHOICES, required=False)
    name = serializers.CharField(required=False)


class DocumentTemplateRenameSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)


class DocumentTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentTemplate
        fields = [
            "id",
            "topic",
            "name",
            "url",
            "created_at",
            "modified_at",
            "files",
        ]

    # read only fields
    name = serializers.CharField(read_only=True)
    url = serializers.CharField(source="file.url", read_only=True)
    created_at = serializers.SerializerMethodField()
    modified_at = serializers.SerializerMethodField()

    # read/write fields
    topic = serializers.ChoiceField(choices=CaseTopic.ACTIVE_CHOICES, required=True)

    # write only fields
    files = serializers.ListField(
        child=serializers.FileField(), allow_empty=False, write_only=True
    )

    def create(self, validated_data):
        files = validated_data.pop("files")
        topic = validated_data.get("topic")

        for file in files:
            DocumentTemplate.objects.create(
                topic=topic,
                file=file,
            )
        return validated_data

    def get_created_at(self, obj):
        try:
            created_at = obj.file.storage.get_created_time(obj.file.name)
            return timezone.localtime(created_at).strftime("%d/%m/%Y")
        except FileNotFoundError:
            return ""

    def get_modified_at(self, obj):
        try:
            modified_at = obj.file.storage.get_modified_time(obj.file.name)
            return timezone.localtime(modified_at).strftime("%d/%m/%Y")
        except FileNotFoundError:
            return ""
