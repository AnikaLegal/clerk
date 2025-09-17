from django.urls import reverse
from django.utils.http import urlencode
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from emails.models import EmailTemplate, Email, EmailAttachment

from .fields import LocalDateField, LocalTimeField
from .user import UserSerializer


class EmailTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailTemplate
        fields = ("id", "name", "topic", "subject", "text", "created_at", "url")
        read_only_fields = ("created_at", "url")

    url = serializers.SerializerMethodField()
    created_at = LocalDateField()

    def get_url(self, obj):
        return reverse("template-email-detail", args=(obj.pk,))


class EmailAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailAttachment
        fields = (
            "id",
            "url",
            "name",
            "email",
            "sharepoint_state",
            "content_type",
            "file",
        )

    file = serializers.FileField(write_only=True)
    url = serializers.URLField(source="file.url", read_only=True)
    name = serializers.CharField(source="file.name", read_only=True)
    sharepoint_state = serializers.CharField(read_only=True)
    content_type = serializers.CharField(read_only=True)

    def create(self, validated_data):
        file = validated_data["file"]
        if file.size / 1024 / 1024 > 30:
            raise ValidationError({"file": "File must be <30MB."})

        data = {
            **validated_data,
            "content_type": file.content_type,
        }
        return super().create(data)


class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Email
        fields = (
            "id",
            "cc_addresses",
            "created_at",
            "processed_at",
            "from_address",
            "html",
            "issue",
            "text",
            "sender",
            "state",
            "subject",
            "to_address",
            "reply_url",
            "attachments",
            "edit_url",
        )

    sender = UserSerializer(read_only=True)
    attachments = EmailAttachmentSerializer(many=True, read_only=True)
    edit_url = serializers.SerializerMethodField()
    reply_url = serializers.SerializerMethodField()
    created_at = LocalTimeField()
    processed_at = LocalTimeField()

    def get_edit_url(self, obj):
        return reverse("case-email-edit", args=(obj.issue.pk, obj.pk))

    def get_reply_url(self, obj):
        return (
            reverse("case-email-draft", args=(obj.issue.pk,))
            + "?"
            + urlencode({"parent": obj.pk})
        )


class EmailThreadSerializer(serializers.Serializer):
    emails = EmailSerializer(many=True)
    subject = serializers.CharField(read_only=True)
    slug = serializers.CharField(read_only=True)
    most_recent = LocalTimeField()
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        return reverse("case-email-thread", args=(obj.issue.pk, obj.slug))
