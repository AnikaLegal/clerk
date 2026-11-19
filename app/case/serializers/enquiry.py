from caller.models import Call
from core.models import Client, Issue
from rest_framework import serializers
from rest_framework.reverse import reverse
from webhooks.models import WebflowContact

EDITABLE_FIELDS = ("requires_callback", "number_callbacks", "comments")


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

    def get_match(self, obj):
        match = self.context.get("client_matches", {}).get(obj.pk)
        return EnquiryMatchSerializer(match).data if match else None


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
            *EDITABLE_FIELDS,
            "match",
        )
        read_only_fields = tuple(f for f in fields if f not in EDITABLE_FIELDS)
        extra_kwargs = {"number_callbacks": {"min_value": 0}}

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
            *EDITABLE_FIELDS,
            "match",
        )
        read_only_fields = tuple(f for f in fields if f not in EDITABLE_FIELDS)
        extra_kwargs = {"number_callbacks": {"min_value": 0}}


class EnquirySearchSerializer(serializers.Serializer):
    requires_callback = serializers.BooleanField(required=False)
