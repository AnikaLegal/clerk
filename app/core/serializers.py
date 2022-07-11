from rest_framework import serializers

from .models import FileUpload, Submission
from emails.admin import NoEmailAdmin


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

class NoEmailAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoEmailAdmin
        fields = (
            "id",
            "name",
            "phone_number",
        )
