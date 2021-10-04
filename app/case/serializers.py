import re

from django.utils.html import strip_tags
from html_sanitizer import Sanitizer
from rest_framework import serializers

from emails.models import Email, EmailAttachment
from accounts.models import User


class EmailAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailAttachment
        fields = [
            "id",
            "file",
        ]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "full_name",
            "email",
        ]

    full_name = serializers.SerializerMethodField()

    def get_full_name(self, user):
        return user.get_full_name()


class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Email
        fields = [
            "id",
            "cc_addresses",
            "created_at",
            "from_address",
            "html",
            "emailattachments",
            "sender",
            "state",
            "subject",
            "to_address",
        ]

    sender = UserSerializer()
    html = serializers.SerializerMethodField()
    emailattachments = EmailAttachmentSerializer(many=True, read_only=True)

    def get_html(self, email):
        if email.html:
            return sanitizer.sanitize(email.html)
        else:
            text = email.text.replace("\r", "")
            text = re.sub("\n(?!\n)", " <br/>", text)
            return "".join(
                [f"<p>{line}</p>" for line in strip_tags(text).split("\n") if line]
            )


sanitizer = Sanitizer(
    {
        "tags": {
            "a",
            "b",
            "blockquote",
            "br",
            "div",
            "em",
            "h1",
            "h2",
            "h3",
            "hr",
            "i",
            "li",
            "ol",
            "p",
            "span",
            "strong",
            "sub",
            "sup",
            "ul",
            "img",
        },
        "attributes": {
            "a": ("href", "name", "target", "title", "id", "rel", "src", "style")
        },
        "empty": {"hr", "a", "br"},
        "separate": {"a", "p", "li"},
        "whitespace": {"br"},
        "keep_typographic_whitespace": False,
        "add_nofollow": False,
        "autolink": False,
    }
)
