from rest_framework import serializers

from questions.models import FileUpload, ImageUpload, Submission


class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ("id", "topic", "complete", "questions", "answers")


class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileUpload
        ready_only_fields = ("id",)
        fields = ("id", "file")


class ImageUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageUpload
        ready_only_fields = ("id",)
        fields = ("id", "image")
