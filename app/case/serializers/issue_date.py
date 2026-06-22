from datetime import date

from core.models import IssueDate
from core.models.issue_date import DateType, HearingType
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
            "hearing_type",
            "hearing_location",
        ]
        extra_kwargs = {
            "notes": {"required": False},
            "is_reviewed": {"required": False},
            "hearing_location": {"required": False, "allow_blank": True},
        }

    issue = IssueSerializer(read_only=True)
    issue_id = serializers.UUIDField(write_only=True, required=True)
    type = serializers.ChoiceField(choices=DateType.choices, required=True)
    hearing_type = serializers.ChoiceField(
        choices=HearingType.choices, required=False, allow_blank=True
    )

    def validate(self, attrs):
        type = attrs.get("type")
        if type and type == DateType.HEARING_LISTED:
            for field_name in ["hearing_type", "hearing_location"]:
                value = attrs.get(field_name)
                if not value:
                    raise serializers.ValidationError(
                        {field_name: self.fields[field_name].error_messages["required"]}
                    )
        return super().validate(attrs)

    def validate_date(self, value):
        # On update, only reject a past date if it is being changed.
        if self.instance is not None and value == self.instance.date:
            return value
        if value < date.today():
            raise serializers.ValidationError("Date cannot be prior to today.")
        return value

    def validate_is_reviewed(self, value):
        # The is_reviewed field is only editable by admins.
        request = self.context.get("request", None)
        if not request or not request.user.is_admin_or_better:
            raise exceptions.PermissionDenied()
        return value

    def validate_issue_id(self, value):
        # Prevent date creation if the related issue is closed.
        from core.models import Issue

        if (
            self.instance is None
            and Issue.objects.filter(id=value, is_open=False).exists()
        ):
            raise serializers.ValidationError(
                "Cannot add a critical date to a closed case."
            )
        return value

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.type != DateType.HEARING_LISTED:
            representation.pop("hearing_type", None)
            representation.pop("hearing_location", None)
        return representation


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
