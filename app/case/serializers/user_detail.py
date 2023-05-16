from rest_framework import serializers

from accounts.models import University, User

from .user import UserSerializer
from .issue import IssueDetailSerializer, IssueNoteSerializer
from .fields import LocalDateField


def university_with_choices(university: University | None, queryset_override=None):
    value = university.name if university is not None else ""
    queryset = (
        queryset_override if queryset_override is not None else University.objects.all()
    )
    return {
        "display": value,
        "value": value,
        "choices": [("", "")] + [(uni.name, uni.name) for uni in queryset],
    }


class UniversityWithChoicesRelatedField(serializers.SlugRelatedField):
    def to_representation(self, obj: University):
        return university_with_choices(obj, queryset_override=self.get_queryset())


class UserDetailSerializer(UserSerializer):
    class Meta:
        model = User
        fields = (
            *UserSerializer.Meta.fields,
            "issue_set",
            "lawyer_issues",
            "performance_notes",
            "ms_account_created_at",
            "university",
        )

    lawyer_issues = IssueDetailSerializer(read_only=True, many=True)
    issue_set = IssueDetailSerializer(read_only=True, many=True)
    performance_notes = serializers.SerializerMethodField()
    ms_account_created_at = LocalDateField()
    university = UniversityWithChoicesRelatedField(
        slug_field="name", queryset=University.objects.all(), allow_null=True
    )

    def get_performance_notes(self, user):
        qs = user.issue_notes.all()
        return IssueNoteSerializer(qs, many=True).data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if representation["university"] is None:
            representation["university"] = university_with_choices(None)
        return representation
