from rest_framework import serializers

from .answers import AnswersSerializer
from .fields import TidyJsonField


class SubmissionSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    answers = AnswersSerializer()
    answers_raw = TidyJsonField(source="answers", read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
