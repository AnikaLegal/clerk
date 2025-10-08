from rest_framework import serializers
from core.services.submission import UPLOAD_ANSWERS


class FileUploadListSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        answers = data.answers
        topic = answers.get("ISSUES")
        if topic:
            upload_answers = UPLOAD_ANSWERS.get(topic, [])
            uploads = []
            for key in upload_answers:
                uploads.extend(answers.get(key) or [])
        else:
            uploads = []
        return super().to_representation(uploads)

    def to_internal_value(self, data):  # pyright: ignore [reportIncompatibleMethodOverride]
        data = super().to_internal_value(data)
        return {"file_uploads": data}


class FileUploadSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    file = serializers.URLField()

    class Meta:
        list_serializer_class = FileUploadListSerializer
