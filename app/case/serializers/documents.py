from rest_framework import serializers

from core.models.issue import CaseTopic


class DocumentTemplateSerializer(serializers.Serializer):
    topic = serializers.ChoiceField(choices=CaseTopic.ACTIVE_CHOICES)
    files = serializers.ListField(child=serializers.FileField(), allow_empty=False)
