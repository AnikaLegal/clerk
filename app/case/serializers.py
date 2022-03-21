from rest_framework import serializers
from django.urls import reverse

from accounts.models import User
from emails.models import EmailTemplate


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "is_intern",
            "is_superuser",
            "created_at",
            "groups",
            "url",
        )
        read_only_fields = ("created_at", "url", "full_name", "groups", "is_superuser")

    url = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()

    def get_groups(self, obj):
        return list(obj.groups.values_list("name", flat=True))

    def get_full_name(self, obj):
        return obj.get_full_name().title()

    def get_created_at(self, obj):
        return obj.created_at.strftime("%d/%m/%Y")

    def get_url(self, obj):
        return reverse("account-user-detail", args=(obj.pk,))


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
