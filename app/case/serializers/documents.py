from core.models import CaseTopic
from core.models.document_template import DocumentTemplate
from rest_framework import serializers


class DocumentTemplateFilterSerializer(serializers.Serializer):
    topic = serializers.ChoiceField(choices=CaseTopic.ACTIVE_CHOICES, required=False)
    name = serializers.CharField(required=False)


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
    id = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    url = serializers.CharField(source="file.url", read_only=True)
    created_at = serializers.DateTimeField(read_only=True, format="%d/%m/%Y")
    modified_at = serializers.DateTimeField(read_only=True, format="%d/%m/%Y")

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
