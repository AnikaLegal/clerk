from rest_framework import serializers

from accounts.models import User

from .user import UserSerializer
from .issue import IssueDetailSerializer, IssueNoteSerializer
from .fields import LocalDateField


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
