from rest_framework import serializers
from core.models.person import SupportContactPreferences
from case.serializers.fields import ChoiceDisplayField


class PersonSerializer(serializers.Serializer):
    name = serializers.CharField(
        allow_null=True, allow_blank=True, trim_whitespace=True
    )
    address = serializers.CharField(
        allow_null=True, allow_blank=True, trim_whitespace=True
    )
    email = serializers.CharField(
        allow_null=True, allow_blank=True, trim_whitespace=True
    )
    phone_number = serializers.CharField(
        allow_null=True, allow_blank=True, trim_whitespace=True
    )
    support_contact_preferences = ChoiceDisplayField(
        allow_null=True, choices=SupportContactPreferences.choices
    )

    def to_representation(self, instance):  # pyright: ignore [reportIncompatibleMethodOverride]
        instance = super().to_representation(instance)
        if all(value is None for value in instance.values()):
            return None
        return instance
