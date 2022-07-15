from rest_framework import serializers
from django.urls import reverse
from django.utils import timezone
from django.utils.http import urlencode

from case.middleware import annotate_group_access
from core.models import Issue, Tenancy, IssueNote, Person, Client
from accounts.models import User
from emails.models import EmailTemplate, Email, EmailAttachment
from core.models.client import (
    CallTime,
    ReferrerType,
    RentalType,
    EligibilityCircumstanceType,
    EmploymentType,
)


class DateField(serializers.ReadOnlyField):
    def to_representation(self, value):
        if not value:
            return None
        else:
            return value.strftime("%d/%m/%y")


class LocalDateField(serializers.ReadOnlyField):
    def to_representation(self, value):
        if not value:
            return None
        else:
            return timezone.localtime(value).strftime("%d/%m/%y")


class LocalTimeField(serializers.ReadOnlyField):
    def to_representation(self, value):
        if not value:
            return None
        else:
            return timezone.localtime(value).strftime("%d/%m/%y at %-I%p")


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "case_capacity",
            "is_intern",
            "is_superuser",
            "created_at",
            "groups",
            "url",
            "is_admin_or_better",
            "is_coordinator_or_better",
            "is_paralegal_or_better",
            "is_admin",
            "is_coordinator",
            "is_paralegal",
            "is_ms_account_set_up",
            "created_at",
        )
        read_only_fields = ("created_at", "url", "full_name", "groups", "is_superuser")

    url = serializers.SerializerMethodField()
    created_at = LocalDateField(source="date_joined")
    full_name = serializers.SerializerMethodField()
    groups = serializers.SerializerMethodField()
    is_admin_or_better = serializers.BooleanField(read_only=True)
    is_coordinator_or_better = serializers.BooleanField(read_only=True)
    is_paralegal_or_better = serializers.BooleanField(read_only=True)
    is_admin = serializers.BooleanField(read_only=True)
    is_coordinator = serializers.BooleanField(read_only=True)
    is_paralegal = serializers.BooleanField(read_only=True)
    is_ms_account_set_up = serializers.SerializerMethodField()

    def to_representation(self, instance):
        if instance:
            annotate_group_access(instance)

        return super().to_representation(instance)

    def get_is_ms_account_set_up(self, obj):
        fifteen_minutes_ago = timezone.now() - timezone.timedelta(minutes=15)
        return obj.ms_account_created_at and (
            obj.ms_account_created_at < fifteen_minutes_ago
        )

    def get_groups(self, obj):
        return [g.name for g in obj.groups.all()]

    def get_full_name(self, obj):
        return obj.get_full_name().title()

    def get_url(self, obj):
        return reverse("account-user-detail", args=(obj.pk,))


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ("id", "full_name", "email", "address", "phone_number", "url")

    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        return reverse("person-detail", args=(obj.pk,))


class TenancySerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenancy
        fields = (
            "address",
            "suburb",
            "postcode",
            "started",
            "is_on_lease",
            "landlord",
            "agent",
            "url",
        )

    landlord = PersonSerializer(read_only=True)
    agent = PersonSerializer(read_only=True)
    url = serializers.SerializerMethodField()
    is_on_lease = serializers.CharField(source="get_is_on_lease_display")
    started = DateField()

    def get_url(self, obj):
        return reverse("tenancy-detail", args=(obj.pk,))


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
            "note_type_display",
            "text",
            "text_display",
            "created_at",
            "event",
            "reviewee",
        )

    creator = UserSerializer(read_only=True)
    text_display = serializers.CharField(source="get_text", read_only=True)
    note_type_display = serializers.CharField(
        source="get_note_type_display", read_only=True
    )
    created_at = serializers.SerializerMethodField()
    reviewee = serializers.SerializerMethodField()
    event = DateField()
    created_at = LocalTimeField()

    def get_reviewee(self, obj):
        if obj.note_type == "PERFORMANCE":
            return UserSerializer(obj.content_object).data


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "date_of_birth",
            "phone_number",
            "employment_status",
            "weekly_income",
            "gender",
            "centrelink_support",
            "eligibility_notes",
            "requires_interpreter",
            "primary_language_non_english",
            "primary_language",
            "is_aboriginal_or_torres_strait_islander",
            "rental_circumstances",
            "number_of_dependents",
            "eligibility_circumstances",
            "referrer_type",
            "referrer",
            "age",
            "full_name",
            "notes",
            "url",
        )

    id = serializers.CharField(read_only=True)
    age = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    date_of_birth = serializers.DateTimeField(
        format="%d/%m/%Y", input_formats=["%d/%m/%Y"]
    )

    def get_url(self, obj):
        return reverse("client-detail", args=(obj.pk,))

    def get_age(self, obj):
        return obj.get_age()

    def get_full_name(self, obj):
        return obj.get_full_name()


class BaseIssueSerializer(serializers.ModelSerializer):
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
            "is_open",
            "is_sharepoint_set_up",
            "actionstep_id",
            "created_at",
            "url",
        )

    id = serializers.CharField(read_only=True)
    lawyer = UserSerializer(read_only=True)
    paralegal = UserSerializer(read_only=True)
    topic_display = serializers.CharField(source="get_topic_display")
    outcome_display = serializers.CharField(source="get_outcome_display")
    stage_display = serializers.CharField(source="get_stage_display")
    created_at = LocalDateField()
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        return reverse("case-detail-view", args=(obj.pk,))


class IssueListSerializer(BaseIssueSerializer):
    class Meta:
        model = Issue
        fields = (*BaseIssueSerializer.Meta.fields,)


class IssueDetailSerializer(BaseIssueSerializer):
    class Meta:
        model = Issue
        fields = (
            *BaseIssueSerializer.Meta.fields,
            "client",
        )

    client = ClientSerializer(read_only=True)


class TextChoiceField(serializers.CharField):
    def __init__(self, text_choice_cls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text_choice_cls = text_choice_cls

    def to_representation(self, value):
        display = self.text_choice_cls[value].label if value else ""
        return {
            "display": display,
            "value": value,
            "choices": self.text_choice_cls.choices,
        }


class TextChoiceListField(serializers.ListField):
    child = serializers.CharField()

    def __init__(self, text_choice_cls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text_choice_cls = text_choice_cls

    def to_representation(self, value):
        display = " | ".join(self.text_choice_cls[s].label for s in value if s)
        return {
            "display": display,
            "value": [v for v in value if v],
            "choices": self.text_choice_cls.choices,
        }


class ParalegalSerializer(UserSerializer):
    class Meta:
        model = User
        fields = (
            *UserSerializer.Meta.fields,
            "latest_issue_created_at",
            "total_cases",
            "open_cases",
            "open_repairs",
            "open_bonds",
            "open_eviction",
            "capacity",
        )

    latest_issue_created_at = LocalDateField()
    total_cases = serializers.IntegerField(read_only=True)
    open_cases = serializers.IntegerField(read_only=True)
    open_repairs = serializers.IntegerField(read_only=True)
    open_bonds = serializers.IntegerField(read_only=True)
    open_eviction = serializers.IntegerField(read_only=True)
    capacity = serializers.IntegerField(read_only=True)


class UserDetailSerializer(UserSerializer):
    class Meta:
        model = User
        fields = (
            *UserSerializer.Meta.fields,
            "issue_set",
            "lawyer_issues",
            "performance_notes",
            "ms_account_created_at",
        )

    lawyer_issues = IssueDetailSerializer(read_only=True, many=True)
    issue_set = IssueDetailSerializer(read_only=True, many=True)
    performance_notes = serializers.SerializerMethodField()
    ms_account_created_at = LocalDateField()

    def get_performance_notes(self, user):
        qs = user.issue_notes.all()
        return IssueNoteSerializer(qs, many=True).data


class ClientDetailSerializer(ClientSerializer):
    class Meta:
        model = Client
        fields = (
            *ClientSerializer.Meta.fields,
            "issue_set",
            "call_times",
        )

    issue_set = IssueListSerializer(read_only=True, many=True)
    # TODO - hoist these fields up into ClientSerializer, fix whatever breaks
    referrer_type = TextChoiceField(ReferrerType)
    call_times = TextChoiceListField(CallTime)
    employment_status = TextChoiceListField(EmploymentType)
    eligibility_circumstances = TextChoiceListField(EligibilityCircumstanceType)
    rental_circumstances = TextChoiceField(RentalType)


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
            "sharepoint_state",
        )

    url = serializers.URLField(source="file.url")
    name = serializers.CharField(source="file.name")


class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Email
        fields = (
            "id",
            "cc_addresses",
            "created_at",
            "from_address",
            "html",
            "text",
            "pk",
            "sender",
            "state",
            "subject",
            "to_address",
            "reply_url",
            "attachments",
            "edit_url",
        )

    sender = UserSerializer(read_only=True)
    attachments = EmailAttachmentSerializer(
        many=True, read_only=True, source="emailattachment_set"
    )
    edit_url = serializers.SerializerMethodField()
    reply_url = serializers.SerializerMethodField()
    created_at = LocalTimeField()

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
