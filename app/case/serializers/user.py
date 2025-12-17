from rest_framework import serializers
from django.urls import reverse
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from case.middleware import annotate_group_access
from accounts.models import User

from .fields import LocalDateField


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "username", "url")

    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        return reverse("account-detail", args=(obj.pk,))

    def validate_email(self, value: str):
        if not value.endswith("@anikalegal.com"):
            raise ValidationError("Can only invite users with an anikalegal.com email.")

        return value

    def validate(self, attrs):
        if attrs["email"] != attrs["username"]:
            raise ValidationError("Username must be the same as email.")
        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "username",
            "case_capacity",
            "is_intern",
            "is_active",
            "is_superuser",
            # Read only stuff
            "full_name",
            "created_at",
            "groups",
            "url",
            "is_admin_or_better",
            "is_coordinator_or_better",
            "is_lawyer_or_better",
            "is_paralegal_or_better",
            "is_admin",
            "is_coordinator",
            "is_lawyer",
            "is_paralegal",
            "is_ms_account_set_up",
            "ms_account_created_at",
        )
        read_only_fields = ("created_at", "url", "full_name", "groups", "is_superuser")

    url = serializers.SerializerMethodField()
    created_at = LocalDateField(source="date_joined")
    full_name = serializers.SerializerMethodField()
    groups = serializers.SerializerMethodField()
    is_admin_or_better = serializers.BooleanField(read_only=True)
    is_coordinator_or_better = serializers.BooleanField(read_only=True)
    is_lawyer_or_better = serializers.BooleanField(read_only=True)
    is_paralegal_or_better = serializers.BooleanField(read_only=True)
    is_admin = serializers.BooleanField(read_only=True)
    is_coordinator = serializers.BooleanField(read_only=True)
    is_lawyer = serializers.BooleanField(read_only=True)
    is_paralegal = serializers.BooleanField(read_only=True)
    is_ms_account_set_up = serializers.SerializerMethodField()
    ms_account_created_at = LocalDateField()

    def to_representation(self, instance):
        if instance:
            annotate_group_access(instance)

        return super().to_representation(instance)

    def get_is_ms_account_set_up(self, obj):
        fifteen_minutes_ago = timezone.now() - timezone.timedelta(minutes=15)
        is_set_up = obj.ms_account_created_at and (
            obj.ms_account_created_at < fifteen_minutes_ago
        )
        return bool(is_set_up)

    def get_groups(self, obj):
        return [g.name for g in obj.groups.all()]

    def get_full_name(self, obj):
        return obj.get_full_name().title()

    def get_url(self, obj):
        return reverse("account-detail", args=(obj.pk,))


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
