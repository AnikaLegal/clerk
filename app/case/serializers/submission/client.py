from core.models.client import (
    AboriginalOrTorresStraitIslander,
    CallTime,
    EligibilityCircumstanceType,
    RequiresInterpreter,
)
from django.db import models
from rest_framework import serializers

from case.serializers.fields import BooleanYesNoDisplayField, ChoiceDisplayField

from .fields import StringOrListField
from .helpers import string_to_date


class SpecialCircumstances(models.TextChoices):
    CENTRELINK = "CENTRELINK", "Centrelink payment or concession card holder"
    FAMILY_VIOLENCE = "FAMILY_VIOLENCE", "Experiencing or at risk of family violence"
    HEALTH_CONDITION = (
        "HEALTH_CONDITION",
        "Long-term health condition or disability that affects work or education",
    )
    MENTAL_ILLNESS_OR_DISABILITY = (
        "MENTAL_ILLNESS_OR_DISABILITY",
        "Mental illness or intellectual disability",
    )
    PUBLIC_HOUSING = "PUBLIC_HOUSING", "Public or community housing"
    REFUGEE = "REFUGEE", "Refugee or asylum seeker status"
    SINGLE_PARENT = "SINGLE_PARENT", "Single parent"


class ClientSerializer(serializers.Serializer):
    first_name = serializers.CharField(
        allow_blank=True, allow_null=True, trim_whitespace=True
    )
    last_name = serializers.CharField(
        allow_blank=True, allow_null=True, trim_whitespace=True
    )
    preferred_name = serializers.CharField(allow_blank=True, allow_null=True)
    email = serializers.CharField(allow_blank=True, trim_whitespace=True)
    date_of_birth = serializers.DateField(allow_null=True)
    phone_number = serializers.CharField(allow_blank=True, allow_null=True)
    gender = serializers.CharField(
        allow_null=True, allow_blank=True, trim_whitespace=True
    )
    centrelink_support = BooleanYesNoDisplayField(allow_null=True)
    eligibility_notes = serializers.CharField(allow_null=True)
    requires_interpreter = ChoiceDisplayField(
        allow_null=True, choices=RequiresInterpreter.choices
    )
    primary_language_non_english = BooleanYesNoDisplayField(allow_null=True)
    primary_language = serializers.CharField(allow_null=True)
    is_aboriginal_or_torres_strait_islander = ChoiceDisplayField(
        allow_null=True, choices=AboriginalOrTorresStraitIslander.choices
    )
    number_of_dependents = serializers.IntegerField(allow_null=True)
    eligibility_circumstances = StringOrListField(
        allow_null=True,
        child=ChoiceDisplayField(choices=EligibilityCircumstanceType.choices),
    )
    call_times = StringOrListField(
        allow_null=True, child=ChoiceDisplayField(choices=CallTime.choices)
    )

    # Legacy fields.
    special_circumstances = StringOrListField(
        allow_null=True,
        read_only=True,
        child=ChoiceDisplayField(choices=SpecialCircumstances.choices),
    )

    def to_representation(self, instance):  # pyright: ignore [reportIncompatibleMethodOverride]
        instance = {
            "first_name": instance.get("FIRST_NAME"),
            "last_name": instance.get("LAST_NAME"),
            "preferred_name": instance.get("PREFERRED_NAME"),
            "email": instance.get("EMAIL"),
            "date_of_birth": string_to_date(instance.get("DOB")),
            "phone_number": instance.get("PHONE"),
            "gender": instance.get("GENDER"),
            "centrelink_support": instance.get("CENTRELINK_SUPPORT"),
            "eligibility_notes": instance.get("ELIGIBILITY_NOTES"),
            "requires_interpreter": instance.get("INTERPRETER"),
            "primary_language_non_english": instance.get("CAN_SPEAK_NON_ENGLISH"),
            "primary_language": instance.get("FIRST_LANGUAGE"),
            "is_aboriginal_or_torres_strait_islander": instance.get(
                "IS_ABORIGINAL_OR_TORRES_STRAIT_ISLANDER"
            ),
            "number_of_dependents": instance.get("NUMBER_OF_DEPENDENTS"),
            "eligibility_circumstances": instance.get("ELIGIBILITY_CIRCUMSTANCES"),
            "special_circumstances": instance.get("SPECIAL_CIRCUMSTANCES"),
            "call_times": instance.get("AVAILABILITY"),
        }
        instance = super().to_representation(instance)
        if all(value is None for value in instance.values()):
            return None
        return instance

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        return {"client": data}
