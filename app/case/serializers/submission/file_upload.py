from rest_framework import serializers
from core.services.submission import UPLOAD_ANSWERS


class FileUploadListSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        issues = data.get("ISSUES")
        if not isinstance(issues, list):
            issues = [issues]

        uploads = []
        for topic in issues:
            upload_answers = UPLOAD_ANSWERS.get(topic, [])
            for key in upload_answers:
                uploads.extend(data.get(key) or [])

        return super().to_representation(uploads)

    def to_internal_value(self, data):  # pyright: ignore [reportIncompatibleMethodOverride]
        data = super().to_internal_value(data)
        return {"file_uploads": data}


class FileUploadSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    file = serializers.URLField()

    class Meta:
        list_serializer_class = FileUploadListSerializer
