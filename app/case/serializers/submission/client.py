from core.models.client import (
    AboriginalOrTorresStraitIslander,
    CallTime,
    ContactRestriction,
    EligibilityCircumstanceType,
    RequiresInterpreter,
)
from rest_framework import serializers

from case.serializers.fields import ChoiceDisplayField

from .fields import StringOrListField
from .helpers import string_to_date


class ClientSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    preferred_name = serializers.CharField(allow_null=True)
    email = serializers.EmailField()
    date_of_birth = serializers.DateField()
    phone_number = serializers.CharField()
    gender = serializers.CharField()
    centrelink_support = serializers.BooleanField()
    eligibility_notes = serializers.CharField(allow_null=True)
    requires_interpreter = ChoiceDisplayField(
        allow_null=True, choices=RequiresInterpreter.choices
    )
    primary_language_non_english = serializers.BooleanField()
    primary_language = serializers.CharField(allow_null=True)
    is_aboriginal_or_torres_strait_islander = ChoiceDisplayField(
        allow_null=True, choices=AboriginalOrTorresStraitIslander.choices
    )
    number_of_dependents = serializers.IntegerField(allow_null=True)
    eligibility_circumstances = StringOrListField(
        allow_null=True,
        child=ChoiceDisplayField(choices=EligibilityCircumstanceType.choices),
    )
    contact_restriction = ChoiceDisplayField(
        allow_null=True, choices=ContactRestriction.choices
    )
    contact_notes = serializers.CharField(allow_null=True)
    notes = serializers.CharField(allow_null=True)
    call_times = StringOrListField(
        allow_null=True, child=ChoiceDisplayField(choices=CallTime.choices)
    )

    def to_representation(self, instance):
        answers = instance.answers
        instance = {
            "first_name": answers.get("FIRST_NAME"),
            "last_name": answers.get("LAST_NAME"),
            "preferred_name": answers.get("PREFERRED_NAME"),
            "email": answers.get("EMAIL"),
            "date_of_birth": string_to_date(answers.get("DOB")),
            "phone_number": answers.get("PHONE"),
            "gender": answers.get("GENDER"),
            "centrelink_support": answers.get("CENTRELINK_SUPPORT"),
            "eligibility_notes": answers.get("ELIGIBILITY_NOTES"),
            "requires_interpreter": answers.get("INTERPRETER"),
            "primary_language_non_english": answers.get("CAN_SPEAK_NON_ENGLISH"),
            "primary_language": answers.get("FIRST_LANGUAGE"),
            "is_aboriginal_or_torres_strait_islander": answers.get(
                "IS_ABORIGINAL_OR_TORRES_STRAIT_ISLANDER"
            ),
            "number_of_dependents": answers.get("NUMBER_OF_DEPENDENTS"),
            "eligibility_circumstances": answers.get("ELIGIBILITY_CIRCUMSTANCES"),
            "call_times": answers.get("AVAILIBILITY"),
        }
        return super().to_representation(instance)

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        return {"client": data}
