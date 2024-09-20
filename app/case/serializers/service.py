from core.models.service import (
    DiscreteServiceType,
    OngoingServiceType,
    Service,
    ServiceCategory,
)
from rest_framework import serializers


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = (
            "id",
            "issue_id",
            "category",
            "type",
            "started_at",
            "finished_at",
            "notes",
        )

    issue_id = serializers.UUIDField()

    def validate(self, data):
        category = data.get("category")
        type = data.get("type")
        if category and type:
            error_message = f"When category is {category}, type must be one of: "
            if category == ServiceCategory.ONGOING and type not in OngoingServiceType:
                raise serializers.ValidationError(
                    {"type": error_message + ", ".join(OngoingServiceType)}
                )
            if category == ServiceCategory.DISCRETE and type not in DiscreteServiceType:
                raise serializers.ValidationError(
                    {"type": error_message + ", ".join(DiscreteServiceType)}
                )
        return data
