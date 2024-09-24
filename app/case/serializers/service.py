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
            "count",
            "notes",
        )

    issue_id = serializers.UUIDField()

    def validate(self, data):
        # Type must belong to a set of choices depending on the category value.
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

        # Count is required for discrete services.
        count = data.get("count")
        if category == ServiceCategory.DISCRETE and not count:
            raise serializers.ValidationError(
                {"count": self.fields["count"].error_messages["required"]}
            )

        # Finish must be after start date.
        started_at = data.get("started_at")
        finished_at = data.get("finished_at")
        if started_at and finished_at and finished_at < started_at:
            raise serializers.ValidationError(
                {"finished_at": "Date must be after the start date"}
            )

        return data


class ServiceSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = (
            "category",
            "type",
        )
        extra_kwargs = {f: {"required": False} for f in fields}
