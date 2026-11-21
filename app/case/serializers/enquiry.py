from django.db import transaction
from django.db.models import F
from django.utils import timezone
from rest_framework import serializers
from rest_framework.reverse import reverse

from core.models import Client, Issue
from enquiry.models import Callback, Enquiry, EnquirySource

# Callbacks and comments change only through logged callbacks.
EDITABLE_FIELDS = ("requires_callback", "name", "email")

PERSON_FIELDS = ("name", "email")


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
            "enquiry",
            "is_answered",
            "purpose",
            "summary",
            "action_items",
            *PERSON_FIELDS,
        )

    # Saved on the enquiry, when a caller gives their details.
    name = serializers.CharField(
        max_length=255, required=False, allow_blank=True, write_only=True
    )
    email = serializers.EmailField(
        max_length=255, required=False, allow_blank=True, write_only=True
    )

    def validate(self, attrs):
        has_person = any(field in attrs for field in PERSON_FIELDS)
        if has_person and attrs["enquiry"].source != EnquirySource.CALL:
            raise serializers.ValidationError(
                "Name and email can only be saved here for a call."
            )
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        person = {
            field: validated_data.pop(field)
            for field in PERSON_FIELDS
            if field in validated_data
        }
        callback = super().create(validated_data)
        # update() rather than save(), which reruns the contact form signals.
        Enquiry.objects.filter(pk=callback.enquiry_id).update(
            number_callbacks=F("number_callbacks") + 1,
            modified_at=timezone.now(),
            **person,
        )
        return callback

    def to_representation(self, instance):
        return CallbackSerializer(instance, context=self.context).data


class CallbackSearchSerializer(serializers.Serializer):
    enquiry = serializers.IntegerField()


class EnquiryMatchClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = (
            "full_name",
            "created_at",
            "url",
            "contact_restriction",
            "contact_restriction_display",
            "contact_notes",
        )

    full_name = serializers.CharField(source="get_full_name")
    contact_restriction = serializers.SerializerMethodField()
    contact_restriction_display = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        return reverse("client-detail", args=(obj.pk,))

    def get_contact_restriction(self, obj):
        return obj.contact_restriction or None

    def get_contact_restriction_display(self, obj):
        if not obj.contact_restriction:
            return None
        return obj.get_contact_restriction_display()


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

    class Meta:
        model = Enquiry
        fields = (
            "id",
            "created_at",
            "modified_at",
            "source",
            "source_display",
            "name",
            "email",
            "phone",
            "topic",
            "topic_display",
            "referral",
            "requires_callback",
            "number_callbacks",
            "comments",
            "match",
            "latest_callback",
        )
        read_only_fields = tuple(f for f in fields if f not in EDITABLE_FIELDS)

    source_display = serializers.CharField(
        source="get_source_display", read_only=True
    )
    topic_display = serializers.CharField(source="get_topic_display", read_only=True)
    # The column has no email validation of its own.
    email = serializers.EmailField(max_length=255, allow_blank=True, required=False)
    match = serializers.SerializerMethodField()
    latest_callback = serializers.SerializerMethodField()

    def validate(self, attrs):
        # A contact typed in both, so neither can be cleared; a caller's are
        # optional.
        if self.instance and self.instance.source == EnquirySource.CONTACT_FORM:
            for field in PERSON_FIELDS:
                if field in attrs and not attrs[field].strip():
                    raise serializers.ValidationError(
                        {field: "A contact form submission needs this."}
                    )
        return attrs

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


class EnquirySearchSerializer(serializers.Serializer):
    requires_callback = serializers.BooleanField(required=False)
    source = serializers.ChoiceField(choices=EnquirySource.choices, required=False)
