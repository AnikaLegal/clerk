from django.db import transaction
from django.db.models import F
from django.utils import timezone
from rest_framework import serializers
from rest_framework.reverse import reverse

from caller.models import Call, Callback
from core.models import Client, Issue
from webhooks.models import WebflowContact

# Callbacks and comments change only through logged callbacks.
EDITABLE_FIELDS = ("requires_callback",)

CALLER_FIELDS = ("caller_name", "caller_email")


class CallbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Callback
        fields = (
            "id",
            "created_at",
            "logged_by_name",
            "is_answered",
            "purpose",
            "summary",
            "action_items",
        )

    logged_by_name = serializers.SerializerMethodField()

    def get_logged_by_name(self, obj):
        return obj.logged_by.get_full_name() if obj.logged_by else None


class CallbackCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Callback
        fields = (
            "call",
            "contact",
            "is_answered",
            "purpose",
            "summary",
            "action_items",
            *CALLER_FIELDS,
        )

    caller_name = serializers.CharField(
        max_length=255, required=False, allow_blank=True, write_only=True
    )
    caller_email = serializers.EmailField(
        max_length=255, required=False, allow_blank=True, write_only=True
    )

    def validate(self, attrs):
        call, contact = attrs.get("call"), attrs.get("contact")
        if bool(call) == bool(contact):
            raise serializers.ValidationError(
                "Log a callback for either a call or a contact form submission."
            )
        if contact and any(field in attrs for field in CALLER_FIELDS):
            raise serializers.ValidationError(
                "Caller details can only be saved on a call."
            )
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        caller = {
            field: validated_data.pop(field)
            for field in CALLER_FIELDS
            if field in validated_data
        }
        callback = super().create(validated_data)
        enquiry = callback.call or callback.contact
        # update() rather than save(), which reruns the contact's alert signal.
        type(enquiry).objects.filter(pk=enquiry.pk).update(
            number_callbacks=F("number_callbacks") + 1,
            modified_at=timezone.now(),
            **caller,
        )
        return callback

    def to_representation(self, instance):
        return CallbackSerializer(instance, context=self.context).data


class CallbackSearchSerializer(serializers.Serializer):
    call = serializers.IntegerField(required=False)
    contact = serializers.IntegerField(required=False)

    def validate(self, attrs):
        if len(attrs) != 1:
            raise serializers.ValidationError("Filter by either call or contact.")
        return attrs


class EnquiryMatchClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ("full_name", "created_at", "url")

    full_name = serializers.CharField(source="get_full_name")
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        return reverse("client-detail", args=(obj.pk,))


class EnquiryMatchCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = (
            "fileref",
            "topic_display",
            "stage_display",
            "closed_at",
            "paralegal_name",
            "url",
        )

    topic_display = serializers.CharField(source="get_topic_display")
    stage_display = serializers.CharField(source="get_stage_display")
    # Annotated by the client matching query.
    closed_at = serializers.DateTimeField(allow_null=True)
    paralegal_name = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()

    def get_paralegal_name(self, obj):
        return obj.paralegal.get_full_name() if obj.paralegal else None

    def get_url(self, obj):
        return reverse("case-detail", args=(obj.pk,))


class EnquiryMatchSerializer(serializers.Serializer):
    state = serializers.CharField()
    matched_on = serializers.ListField(child=serializers.CharField())
    client = EnquiryMatchClientSerializer()
    case = EnquiryMatchCaseSerializer(allow_null=True)


class EnquirySerializer(serializers.ModelSerializer):
    """
    The view finds client matches for a whole page at once and passes them
    in the "client_matches" context, keyed by enquiry id.
    """

    match = serializers.SerializerMethodField()
    latest_callback = serializers.SerializerMethodField()

    def get_match(self, obj):
        match = self.context.get("client_matches", {}).get(obj.pk)
        return EnquiryMatchSerializer(match).data if match else None

    def get_latest_callback(self, obj):
        # The view prefetches callbacks newest first as callback_list.
        callbacks = getattr(obj, "callback_list", None)
        if callbacks is None:
            callbacks = obj.callbacks.select_related("logged_by").order_by(
                "-created_at"
            )
        latest = next(iter(callbacks), None)
        return CallbackSerializer(latest).data if latest else None


class CallSerializer(EnquirySerializer):
    class Meta:
        model = Call
        fields = (
            "id",
            "created_at",
            "modified_at",
            "phone_number",
            "topic",
            "topic_display",
            *CALLER_FIELDS,
            "requires_callback",
            "number_callbacks",
            "comments",
            "match",
            "latest_callback",
        )
        # Staff can correct the caller's details without logging a call.
        read_only_fields = tuple(
            f for f in fields if f not in (*EDITABLE_FIELDS, *CALLER_FIELDS)
        )

    topic_display = serializers.CharField(source="get_topic_display", read_only=True)


class ContactSerializer(EnquirySerializer):
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
            "requires_callback",
            "number_callbacks",
            "comments",
            "match",
            "latest_callback",
        )
        # Staff can correct what the person typed, or switch their email.
        read_only_fields = tuple(
            f for f in fields if f not in (*EDITABLE_FIELDS, "name", "email")
        )

    # The column has no email validation of its own.
    email = serializers.EmailField(max_length=255)


class EnquirySearchSerializer(serializers.Serializer):
    requires_callback = serializers.BooleanField(required=False)
