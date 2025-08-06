from rest_framework import serializers
from core.models import IssueDate
from core.models.issue_date import DateType
from case.serializers.issue import IssueSerializer


class IssueDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = IssueDate
        fields = [
            "id",
            "issue",
            "issue_id",
            "creator_id",
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


class IssueDateSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = IssueDate
        fields = (
            "type",
            "issue",
            "is_reviewed",
            "q",
        )
        extra_kwargs = {f: {"required": False} for f in fields}

    issue = serializers.UUIDField()
    type = serializers.ChoiceField(choices=DateType.choices)

    # Generic search field - not part of the model.
    q = serializers.CharField(required=False)
