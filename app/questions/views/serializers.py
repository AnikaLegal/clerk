from rest_framework import serializers

from questions.models import Submission, ImageUpload


class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ("id", "data", "complete")


class ImageUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageUpload
        ready_only_fields = ("id",)
        fields = ("id", "image")
