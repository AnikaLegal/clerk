from rest_framework import serializers

from questions.models import ImageUpload, Submission


class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ("id", "complete", "questions", "answers")


class ImageUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageUpload
        ready_only_fields = ("id",)
        fields = ("id", "image")
