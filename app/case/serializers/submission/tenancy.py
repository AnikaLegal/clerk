from core.models.tenancy import LeaseType, RentalType
from rest_framework import serializers

from case.serializers.fields import ChoiceDisplayField

from .person import PersonSerializer
from .helpers import string_to_date


class TenancySerializer(serializers.Serializer):
    address = serializers.CharField(
        allow_null=True, allow_blank=True, trim_whitespace=True
    )
    suburb = serializers.CharField(allow_null=True)
    postcode = serializers.CharField(allow_null=True)
    is_on_lease = ChoiceDisplayField(allow_null=True, choices=LeaseType.choices)
    rental_circumstances = ChoiceDisplayField(
        allow_null=True, choices=RentalType.choices
    )
    start_date = serializers.DateField(allow_null=True)
    landlord = PersonSerializer(allow_null=True)
    agent = PersonSerializer(allow_null=True)

    def to_representation(self, instance):  # pyright: ignore [reportIncompatibleMethodOverride]
        instance = {
            "address": instance.get("ADDRESS"),
            "suburb": instance.get("SUBURB"),
            "postcode": instance.get("POSTCODE"),
            "is_on_lease": instance.get("IS_ON_LEASE"),
            "rental_circumstances": instance.get("RENTAL_CIRCUMSTANCES"),
            "start_date": string_to_date(instance.get("START_DATE")),
            "landlord": {
                "name": instance.get("LANDLORD_NAME"),
                "address": instance.get("LANDLORD_ADDRESS"),
                "email": instance.get("LANDLORD_EMAIL"),
                "phone_number": instance.get("LANDLORD_PHONE"),
            },
            "agent": {
                "name": instance.get("AGENT_NAME"),
                "address": instance.get("AGENT_ADDRESS"),
                "email": instance.get("AGENT_EMAIL"),
                "phone_number": instance.get("AGENT_PHONE"),
            },
        }
        instance = super().to_representation(instance)
        if all(value is None for value in instance.values()):
            return None
        return instance

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        return {"tenancy": data}
