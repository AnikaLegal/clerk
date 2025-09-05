from datetime import date

from core.models import IssueDate
from core.models.issue_date import DateType
from rest_framework import exceptions, serializers

from case.serializers.issue import IssueSerializer


class IssueDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = IssueDate
        fields = [
            "id",
            "issue",
            "issue_id",
            "type",
            "date",
            "notes",
            "is_reviewed",
        ]
        extra_kwargs = {
            "notes": {"required": False},
            "is_reviewed": {"required": False},
        }

    issue = IssueSerializer(read_only=True)
    issue_id = serializers.UUIDField(write_only=True, required=True)
    type = serializers.ChoiceField(choices=DateType.choices, required=True)

    def validate_date(self, value):
        if value < date.today():
            raise serializers.ValidationError("Date cannot be prior to today.")
        return value

    def update(self, instance, validated_data):
        if "is_reviewed" in validated_data:
            request = self.context.get("request", None)
            if not request or not request.user.is_admin_or_better:
                raise exceptions.PermissionDenied()
        return super().update(instance, validated_data)

    def create(self, validated_data):
        if "is_reviewed" in validated_data:
            request = self.context.get("request", None)
            if not request or not request.user.is_admin_or_better:
                raise exceptions.PermissionDenied()
        return super().create(validated_data)


class IssueDateSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = IssueDate
        fields = (
            "type",
            "issue_id",
            "is_reviewed",
            "q",
        )
        extra_kwargs = {f: {"required": False} for f in fields}

    issue_id = serializers.UUIDField()
    type = serializers.ChoiceField(choices=DateType.choices)

    # Generic search field - not part of the model.
    q = serializers.CharField(required=False)
