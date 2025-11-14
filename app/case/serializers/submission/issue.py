from rest_framework import serializers
from core.models.issue import CaseTopic, EmploymentType, ReferrerType
from case.serializers.fields import ChoiceDisplayField
from .fields import StringOrListField
from .person import PersonSerializer


class IssueSerializer(serializers.Serializer):
    issues = StringOrListField(
        allow_null=True, child=ChoiceDisplayField(choices=CaseTopic.CHOICES)
    )
    weekly_income = serializers.IntegerField(allow_null=True)
    employment_status = StringOrListField(
        allow_null=True, child=ChoiceDisplayField(choices=EmploymentType.choices)
    )
    referrer = serializers.CharField(allow_null=True)
    referrer_type = ChoiceDisplayField(allow_null=True, choices=ReferrerType.choices)
    weekly_rent = serializers.IntegerField(allow_null=True)
    support_worker = PersonSerializer(allow_null=True)

    def to_representation(self, instance):  # pyright: ignore [reportIncompatibleMethodOverride]
        instance = {
            "issues": instance.get("ISSUES"),
            "weekly_income": instance.get("WEEKLY_HOUSEHOLD_INCOME")
            or instance.get("WEEKLY_INCOME_MULTI")  # NB legacy value
            or instance.get("WEEKLY_INCOME"),  # NB legacy value
            "employment_status": instance.get("WORK_OR_STUDY_CIRCUMSTANCES"),
            "referrer": instance.get("SOCIAL_REFERRER")
            or instance.get("COMMUNITY_ORGANISATION_REFERRER")
            or instance.get("HOUSING_SERVICE_REFERRER")
            or instance.get("LEGAL_CENTRE_REFERRER"),
            "referrer_type": instance.get("REFERRER_TYPE"),
            "weekly_rent": instance.get("WEEKLY_RENT")
            or instance.get("WEEKLY_RENT_MULTI"),  # NB legacy value
            "support_worker": {
                "name": instance.get("SUPPORT_WORKER_NAME"),
                "address": instance.get("SUPPORT_WORKER_ADDRESS"),
                "email": instance.get("SUPPORT_WORKER_EMAIL"),
                "phone_number": instance.get("SUPPORT_WORKER_PHONE"),
                "support_contact_preferences": instance.get(
                    "SUPPORT_WORKER_CONTACT_PREFERENCE"
                ),
            },
        }
        instance = super().to_representation(instance)
        if all(value is None for value in instance.values()):
            return None
        return instance

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        return {"issue": data}
