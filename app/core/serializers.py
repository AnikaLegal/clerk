from rest_framework import serializers

from core.models import Client, Person, Submission, Tenancy, FileUpload


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
        fields = ("id", "file", "submission")


class TenancySerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenancy
        fields = (
            "client",
            "address",
            "started",
            "is_on_lease",
            "landlord",
            "agent",
        )

    landlord = PersonSerializer()
    agent = PersonSerializer()


class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ("id", "topic", "complete", "answers", "client", "file_uploads")

    file_uploads = FileUploadSerializer(many=True, read_only=True)


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
            "submissions",
            "tenancy",
        )

    tenancy = TenancySerializer(read_only=True)
    submissions = SubmissionSerializer(many=True, read_only=True)
