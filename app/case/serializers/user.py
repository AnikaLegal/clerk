from rest_framework import serializers
from django.urls import reverse
from django.utils import timezone

from case.middleware import annotate_group_access
from accounts.models import User

from .fields import LocalDateField


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "full_name",
            "is_active",
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
