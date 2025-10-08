from rest_framework import serializers
from core.models.issue import CaseTopic, EmploymentType, ReferrerType
from case.serializers.fields import ChoiceDisplayField
from .fields import StringOrListField


class IssueSerializer(serializers.Serializer):
    topic = ChoiceDisplayField(choices=CaseTopic.CHOICES, allow_null=True)

    weekly_rent = serializers.IntegerField(allow_null=True)
    weekly_income = serializers.IntegerField(allow_null=True)
    employment_status = StringOrListField(
        allow_null=True, child=ChoiceDisplayField(choices=EmploymentType.choices)
    )
    referrer_type = ChoiceDisplayField(allow_null=True, choices=ReferrerType.choices)
    referrer = serializers.CharField(allow_null=True)

    def to_representation(self, instance):
        answers = instance.answers
        instance = {
            "topic": answers.get("ISSUES"),
            "weekly_income": answers.get("WEEKLY_HOUSEHOLD_INCOME"),
            "employment_status": answers.get("WORK_OR_STUDY_CIRCUMSTANCES"),
            "referrer": answers.get("SOCIAL_REFERRER")
            or answers.get("COMMUNITY_ORGANISATION_REFERRER")
            or answers.get("HOUSING_SERVICE_REFERRER")
            or answers.get("LEGAL_CENTER_REFERRER"),
            "referrer_type": answers.get("REFERRER_TYPE"),
            "weekly_rent": answers.get("WEEKLY_RENT"),
            "support_worker": {
                "name": answers.get("SUPPORT_WORKER_NAME"),
                "address": answers.get("SUPPORT_WORKER_ADDRESS"),
                "email": answers.get("SUPPORT_WORKER_EMAIL"),
                "phone": answers.get("SUPPORT_WORKER_PHONE"),
                "support_contact_preferences": answers.get(
                    "SUPPORT_WORKER_CONTACT_PREFERENCES"
                ),
            },
        }
        return super().to_representation(instance)

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        return {"issue": data}
