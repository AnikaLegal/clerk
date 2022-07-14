from rest_framework import serializers

from .models import NoEmailSubmission

class NoEmailSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoEmailSubmission
        fields = (
            "id",
            "answers",
        )