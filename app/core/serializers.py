from rest_framework import serializers

from core.models import Client, Person, Issue, Tenancy, FileUpload


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = (
            "id",
            "full_name",
            "email",
            "company",
            "address",
            "phone_number",
        )


class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileUpload
        fields = ("id", "file", "issue")


class TenancySerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenancy
        fields = (
            "id",
            "client",
            "address",
            "started",
            "is_on_lease",
            "landlord",
            "agent",
        )

    landlord = PersonSerializer(read_only=True)
    agent = PersonSerializer(read_only=True)


class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = (
            "id",
            "topic",
            "is_answered",
            "is_submitted",
            "answers",
            "client",
            "fileupload_set",
        )

    fileupload_set = FileUploadSerializer(many=True, read_only=True)


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
            "call_time",
            "is_eligible",
            "issue_set",
            "tenancy_set",
        )

    tenancy_set = TenancySerializer(many=True, read_only=True)
    issue_set = IssueSerializer(many=True, read_only=True)
