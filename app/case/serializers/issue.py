from rest_framework import serializers
from django.urls import reverse
from django.utils import timezone

from core.models import Issue, IssueNote
from accounts.models import User

from .user import UserSerializer
from .client import ClientSerializer
from .person import PersonSerializer
from .fields import DateField, LocalTimeField, LocalDateField


class IssueNoteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = IssueNote
        fields = (
            "creator",
            "note_type",
            "text",
            "issue",
            "event",
        )


class IssueNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = IssueNote
        fields = (
            "id",
            "creator",
            "note_type",
            "text",
            "text_display",
            "created_at",
            "event",
            "reviewee",
        )

    creator = UserSerializer(read_only=True)
    text_display = serializers.CharField(source="get_text", read_only=True)
    reviewee = serializers.SerializerMethodField()
    event = DateField()
    created_at = LocalTimeField()

    def get_reviewee(self, obj):
        if obj.note_type == "PERFORMANCE":
            return UserSerializer(obj.content_object).data


class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = (
            "id",
            "topic",
            "topic_display",
            "stage_display",
            "stage",
            "outcome",
            "outcome_display",
            "outcome_notes",
            "provided_legal_services",
            "fileref",
            "paralegal",
            "lawyer",
            "client",
            "support_worker",
            "is_open",
            "is_sharepoint_set_up",
            "actionstep_id",
            "created_at",
            "url",
            # Case review fields.
            "is_conflict_check",
            "is_eligibility_check",
            "next_review",
        )

    id = serializers.CharField(read_only=True)
    lawyer = UserSerializer(read_only=True)
    paralegal = UserSerializer(read_only=True)
    client = ClientSerializer(read_only=True)
    support_worker = PersonSerializer(read_only=True)
    topic_display = serializers.CharField(source="get_topic_display")
    outcome_display = serializers.CharField(source="get_outcome_display")
    stage_display = serializers.CharField(source="get_stage_display")
    created_at = LocalDateField()
    url = serializers.SerializerMethodField()
    # Case review fields.
    is_conflict_check = serializers.SerializerMethodField()
    is_eligibility_check = serializers.SerializerMethodField()
    next_review = serializers.SerializerMethodField()

    def get_url(self, obj):
        return reverse("case-detail-view", args=(obj.pk,))

    def get_is_conflict_check(self, obj):
        return getattr(obj, "is_conflict_check", None)

    def get_is_eligibility_check(self, obj):
        return getattr(obj, "is_eligibility_check", None)

    def get_next_review(self, obj):
        next_review = getattr(obj, "next_review", None)
        return next_review.strftime("%d/%m/%y") if next_review else None


class IssueAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = ("paralegal", "lawyer")

    def get_fields(self, *args, **kwargs):
        fields = super().get_fields(*args, **kwargs)
        fifteen_minutes_ago = timezone.now() - timezone.timedelta(minutes=15)
        # Wait 15 mins for Sharepoint data sync
        fields["paralegal"].queryset = fields["paralegal"].queryset.filter(
            ms_account_created_at__lte=fifteen_minutes_ago
        )
        return fields

    paralegal = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(groups__name="Paralegal"), allow_null=True
    )
    lawyer = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(groups__name="Lawyer"), allow_null=True
    )


class IssueSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = (
            "topic",
            "stage",
            "outcome",
            "is_open",
            "lawyer",
            "paralegal",
            "search",
        )
        extra_kwargs = {f: {"required": False} for f in fields}

    search = serializers.CharField(required=False)
