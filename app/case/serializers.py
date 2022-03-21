from rest_framework import serializers
from django.urls import reverse

from emails.models import EmailTemplate


class EmailTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailTemplate
        fields = ("id", "name", "topic", "subject", "text", "created_at", "url")
        read_only_fields = ("created_at", "url")

    url = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()

    def get_url(self, obj):
        return reverse("template-email-detail", args=(obj.pk,))

    def get_created_at(self, obj):
        return obj.created_at.strftime("%d/%m/%Y")
