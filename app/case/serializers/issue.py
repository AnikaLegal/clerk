from accounts.models import User
from core.models import Client, Issue, IssueNote, Service, Tenancy
from core.models.issue import CaseStage, EmploymentType, ReferrerType
from core.models.service import ServiceCategory
from django.db import transaction
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from rest_framework import serializers

from .client import ClientSerializer
from .fields import (
    LocalDateField,
    LocalTimeField,
    TextChoiceField,
    TextChoiceListField,
)
from .person import PersonSerializer
from .tenancy import TenancySerializer
from .user import UserSerializer


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
            "answers",
            "paralegal",
            "paralegal_id",
            "lawyer",
            "lawyer_id",
            "client",
            "client_id",
            "tenancy",
            "tenancy_id",
            "employment_status",
            "weekly_income",
            "weekly_rent",
            "referrer_type",
            "referrer",
            "support_worker",
            "support_worker_id",
            "is_open",
            "is_sharepoint_set_up",
            "actionstep_id",
            "submission_id",
            "created_at",
            "url",
            # Case review fields.
            "is_conflict_check",
            "is_eligibility_check",
            "next_review",
        )

    id = serializers.CharField(read_only=True)

    lawyer = UserSerializer(read_only=True)
    lawyer_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=User.objects.filter(groups__name="Lawyer"),
        allow_null=True,
        required=False,
    )

    paralegal = UserSerializer(read_only=True)
    paralegal_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=User.objects.filter(groups__name="Paralegal"),
        allow_null=True,
        required=False,
    )

    client = ClientSerializer(required=False)
    client_id = serializers.UUIDField(write_only=True, required=False)

    tenancy = TenancySerializer(required=False)
    tenancy_id = serializers.IntegerField(write_only=True, required=False)

    support_worker = PersonSerializer(read_only=True)
    support_worker_id = serializers.IntegerField(
        write_only=True, allow_null=True, required=False
    )

    topic_display = serializers.CharField(source="get_topic_display", read_only=True)
    outcome_display = serializers.CharField(
        source="get_outcome_display", read_only=True
    )
    stage_display = serializers.CharField(source="get_stage_display", read_only=True)
    created_at = LocalDateField()
    employment_status = TextChoiceListField(EmploymentType, required=False)
    referrer_type = TextChoiceField(ReferrerType, required=False)

    # Submission-related fields.
    submission_id = serializers.UUIDField(read_only=True)
    answers = serializers.JSONField(read_only=True)

    url = serializers.SerializerMethodField()
    # Case review fields.
    is_conflict_check = serializers.SerializerMethodField()
    is_eligibility_check = serializers.SerializerMethodField()
    next_review = serializers.SerializerMethodField()

    def get_fields(self, *args, **kwargs):
        fields = super().get_fields(*args, **kwargs)
        fifteen_minutes_ago = timezone.now() - timezone.timedelta(minutes=15)
        # Wait 15 mins for Sharepoint data sync
        fields["paralegal_id"].queryset = fields["paralegal_id"].queryset.filter(
            ms_account_created_at__lte=fifteen_minutes_ago
        )
        return fields

    def validate(self, attrs):
        if attrs.get("stage") == CaseStage.CLOSED and self.instance:
            query = Q(
                issue_id=self.instance.id,
                category=ServiceCategory.ONGOING,
                finished_at__isnull=True,
                is_deleted=False,
            )
            if Service.objects.filter(query).exists():
                raise serializers.ValidationError(
                    "Cannot close case with unfinished ongoing services"
                )
        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            data = validated_data.pop("client", None)
            if data:
                instance = Client.objects.create(**data)
                validated_data["client_id"] = instance.pk

            data = validated_data.pop("tenancy", None)
            if data:
                instance = Tenancy.objects.create(**data)
                validated_data["tenancy_id"] = instance.pk

            return super().create(validated_data)

    def validate_paralegal_id(self, paralegal: User):
        return paralegal.id if paralegal else None

    def validate_lawyer_id(self, lawyer: User):
        return lawyer.id if lawyer else None

    def get_url(self, obj):
        return reverse("case-detail", args=(obj.pk,))

    def get_is_conflict_check(self, obj):
        return getattr(obj, "is_conflict_check", None)

    def get_is_eligibility_check(self, obj):
        return getattr(obj, "is_eligibility_check", None)

    def get_next_review(self, obj):
        next_review = getattr(obj, "next_review", None)
        return next_review.strftime("%d/%m/%y") if next_review else None


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
            "client",
            "search",
        )
        extra_kwargs = {f: {"required": False} for f in fields}

    client = serializers.UUIDField(required=False)
    search = serializers.CharField(required=False)


class CreatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "full_name",
            "url",
        )

    url = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()

    def get_full_name(self, obj):
        return obj.get_full_name().title()

    def get_url(self, obj):
        return reverse("account-detail", args=(obj.pk,))


class IssueNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = IssueNote
        fields = (
            "id",
            "creator",
            "creator_id",
            "note_type",
            "text",
            "text_display",
            "created_at",
            "issue_id",
            "event",
            "reviewee",
        )

    creator = CreatorSerializer(read_only=True)
    creator_id = serializers.IntegerField(write_only=True)
    text_display = serializers.CharField(source="get_text", read_only=True)
    reviewee = serializers.SerializerMethodField()
    issue_id = serializers.UUIDField(write_only=True)
    event = serializers.DateTimeField(required=False)
    created_at = LocalTimeField()

    def get_reviewee(self, obj):
        if obj.note_type == "PERFORMANCE":
            return UserSerializer(obj.content_object).data


class IssueNoteSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = IssueNote
        fields = (
            "issue",
            "creator",
            "note_type",
            "reviewee",
        )
        extra_kwargs = {f: {"required": False} for f in fields}

    issue = serializers.UUIDField(required=False)
    reviewee = serializers.CharField(required=False)
