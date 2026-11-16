from caller.models import Call
from core.models.issue import CaseTopic
from rest_framework import serializers
from webhooks.models import WebflowContact

EDITABLE_FIELDS = ("requires_callback", "number_callbacks", "comments")


class CallSerializer(serializers.ModelSerializer):
    class Meta:
        model = Call
        fields = (
            "id",
            "created_at",
            "modified_at",
            "phone_number",
            "topic",
            "topic_display",
            *EDITABLE_FIELDS,
        )
        read_only_fields = tuple(f for f in fields if f not in EDITABLE_FIELDS)
        extra_kwargs = {"number_callbacks": {"min_value": 0}}

    topic_display = serializers.CharField(source="get_topic_display", read_only=True)


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebflowContact
        fields = (
            "id",
            "created_at",
            "modified_at",
            "name",
            "email",
            "phone",
            "referral",
            *EDITABLE_FIELDS,
        )
        read_only_fields = tuple(f for f in fields if f not in EDITABLE_FIELDS)
        extra_kwargs = {"number_callbacks": {"min_value": 0}}


class CallSearchSerializer(serializers.Serializer):
    requires_callback = serializers.BooleanField(required=False)
    topic = serializers.ChoiceField(choices=CaseTopic.CHOICES, required=False)


class ContactSearchSerializer(serializers.Serializer):
    requires_callback = serializers.BooleanField(required=False)
