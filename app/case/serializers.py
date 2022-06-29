from rest_framework import serializers
from django.urls import reverse
from django.utils import timezone

from core.models import Issue, Tenancy, IssueNote, Person, Client
from accounts.models import User
from emails.models import EmailTemplate


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "is_intern",
            "is_superuser",
            "created_at",
            "groups",
            "url",
        )
        read_only_fields = ("created_at", "url", "full_name", "groups", "is_superuser")

    url = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    groups = serializers.SerializerMethodField()

    def get_groups(self, obj):
        return [g.name for g in obj.groups.all()]

    def get_full_name(self, obj):
        return obj.get_full_name().title()

    def get_created_at(self, obj):
        return obj.date_joined.strftime("%d/%m/%Y")

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
    started = serializers.SerializerMethodField()
    is_on_lease = serializers.CharField(source="get_is_on_lease_display")

    def get_started(self, obj):
        return obj.started.strftime("%d/%m/%Y")

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
    event = serializers.SerializerMethodField()
    reviewee = serializers.SerializerMethodField()

    def get_reviewee(self, obj):
        if obj.note_type == "PERFORMANCE":
            return UserSerializer(obj.content_object).data

    def get_event(self, obj):
        return obj.event.strftime("%d/%m/%Y") if obj.event else None

    def get_created_at(self, obj):
        return obj.created_at.strftime("%d/%m/%Y")


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
            #"special_circumstances", - Not in use
            # Not in use
            #"weekly_income",
            #"weekly_rent",
            "gender",
            "primary_language_non_english",
            "interpreter",
            "primary_language",
            "is_aboriginal_or_torres_strait_islander",
            "legal_access_and_special_circumstances",
            "rental_circumstances",
            #"is_multi_income_household", - Not in use
            "weekly_household_income",
            "dependents",
            #"number_of_dependents", - Not in use
            #"legal_access_difficulties", - Not in use
            "referrer_type",
            "referrer",
            "centrelink_support",
            "age",
            "full_name",
            "url",
        )

    id = serializers.CharField(read_only=True)
    age = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        return reverse("client-detail", args=(obj.pk,))

    def get_age(self, obj):
        return obj.get_age()

    def get_full_name(self, obj):
        return obj.get_full_name()


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
            "client",
            "paralegal",
            "lawyer",
            "is_open",
            "is_sharepoint_set_up",
            "actionstep_id",
            "created_at",
        )

    id = serializers.CharField(read_only=True)
    client = ClientSerializer(read_only=True)
    lawyer = UserSerializer(read_only=True)
    paralegal = UserSerializer(read_only=True)
    topic_display = serializers.CharField(source="get_topic_display")
    outcome_display = serializers.CharField(source="get_outcome_display")
    stage_display = serializers.CharField(source="get_stage_display")
    created_at = serializers.SerializerMethodField()

    def get_created_at(self, obj):
        return obj.created_at.strftime("%d/%m/%Y")


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
    created_at = serializers.SerializerMethodField()

    def get_url(self, obj):
        return reverse("template-email-detail", args=(obj.pk,))

    def get_created_at(self, obj):
        return obj.created_at.strftime("%d/%m/%Y")
