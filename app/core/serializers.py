from rest_framework import serializers

from .models import FileUpload, Submission


class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = (
            "id",
            "answers",
        )


class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileUpload
        fields = ("id", "file", "issue")
