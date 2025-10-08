from rest_framework import serializers
from core.models.person import SupportContactPreferences
from case.serializers.fields import ChoiceDisplayField


class PersonSerializer(serializers.Serializer):
    name = serializers.CharField(allow_null=True)
    address = serializers.CharField(allow_null=True)
    email = serializers.EmailField(allow_null=True)
    phone = serializers.CharField(allow_null=True)
    support_contact_preferences = ChoiceDisplayField(
        allow_null=True, choices=SupportContactPreferences.choices
    )
