from rest_framework import serializers

from .client import ClientSerializer
from .file_upload import FileUploadSerializer
from .issue import IssueSerializer
from .tenancy import TenancySerializer


class SubmissionSerializer(serializers.Serializer):
    client = ClientSerializer(source="*", partial=True)
    tenancy = TenancySerializer(source="*", partial=True)
    issue = IssueSerializer(source="*", partial=True)
    file_uploads = FileUploadSerializer(source="*", partial=True, many=True)
    answers = serializers.JSONField(read_only=True)
