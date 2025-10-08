from datetime import datetime

from core.models.tenancy import LeaseType, RentalType
from rest_framework import serializers

from case.serializers.fields import ChoiceDisplayField

from .person import PersonSerializer


class TenancySerializer(serializers.Serializer):
    address = serializers.CharField()
    suburb = serializers.CharField(allow_null=True)
    postcode = serializers.CharField(allow_null=True)
    is_on_lease = ChoiceDisplayField(allow_null=True, choices=LeaseType.choices)
    rental_circumstances = ChoiceDisplayField(
        allow_null=True, choices=RentalType.choices
    )
    start_date = serializers.DateField(
        allow_null=True,
        format="%d/%m/%Y",  # pyright: ignore[reportArgumentType]
        input_formats=["%d/%m/%Y"],
    )
    landlord = PersonSerializer(allow_null=True)
    agent = PersonSerializer(allow_null=True)

    def to_representation(self, instance):
        answers = instance.answers
        instance = {
            "address": answers.get("ADDRESS"),
            "suburb": answers.get("SUBURB"),
            "postcode": answers.get("POSTCODE"),
            "is_on_lease": answers.get("IS_ON_LEASE"),
            "rental_circumstances": answers.get("RENTAL_CIRCUMSTANCES"),
            "start_date": datetime.strptime(
                answers.get("START_DATE"), "%Y-%m-%d"
            ).date(),
            "landlord": {
                "name": answers.get("LANDLORD_NAME"),
                "address": answers.get("LANDLORD_ADDRESS"),
                "email": answers.get("LANDLORD_EMAIL"),
                "phone": answers.get("LANDLORD_PHONE"),
            },
            "agent": {
                "name": answers.get("AGENT_NAME"),
                "address": answers.get("AGENT_ADDRESS"),
                "email": answers.get("AGENT_EMAIL"),
                "phone": answers.get("AGENT_PHONE"),
            },
        }
        return super().to_representation(instance)

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        return {"tenancy": data}
