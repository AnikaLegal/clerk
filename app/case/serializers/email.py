from django.urls import reverse
from django.utils.http import urlencode
from emails.models import Email, EmailAttachment, EmailState, EmailTemplate
from emails.utils.size import (
    MAX_EMAIL_SIZE_BYTES,
    base64_size,
    format_size,
    get_email_payload_size,
)
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

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
        email = validated_data.get("email")

        # SendGrid limits the total size of the message and all attachments, so
        # validate the cumulative size of the existing attachments plus this new
        # one (after base64 encoding) rather than this file in isolation.
        if email is not None:
            used = get_email_payload_size(
                email.text, email.html, email.attachments.all()
            )
            if used + base64_size(file.size) > MAX_EMAIL_SIZE_BYTES:
                # Attachments are base64 encoded (~33% larger) for delivery, so
                # the raw space left for this file is the encoded headroom
                # scaled back down by that ratio.
                remaining = max(0, (MAX_EMAIL_SIZE_BYTES - used) * 3 // 4)
                raise ValidationError(
                    {
                        "file": f"File too large. {format_size(remaining)} of "
                        "attachment space left on this email."
                    }
                )

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

    def validate(self, attrs):
        # When an email is marked ready to send, ensure the total message size
        # (body + all attachments, base64 encoded) is within SendGrid's limit.
        if attrs.get("state") == EmailState.READY_TO_SEND and self.instance:
            size = get_email_payload_size(
                attrs.get("text", self.instance.text),
                attrs.get("html", self.instance.html),
                self.instance.attachments.all(),
            )
            if size > MAX_EMAIL_SIZE_BYTES:
                raise ValidationError(
                    f"Email too large to send ({format_size(size)} when encoded for delivery, "
                    f"over the {format_size(MAX_EMAIL_SIZE_BYTES)} limit). Remove or shrink "
                    "an attachment and try again."
                )
        return attrs

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
