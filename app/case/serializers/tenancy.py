from rest_framework import serializers
from django.urls import reverse

from core.models.tenancy import Tenancy, LeaseType, RentalType
from .person import PersonSerializer
from .fields import TextChoiceField


class TenancySerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenancy
        fields = (
            "id",
            "address",
            "suburb",
            "postcode",
            "started",
            "is_on_lease",
            "rental_circumstances",
            "landlord",
            "agent",
            "landlord_id",
            "agent_id",
            "url",
        )

    suburb = serializers.CharField(required=True)
    postcode = serializers.CharField(required=True)

    landlord = PersonSerializer(read_only=True)
    landlord_id = serializers.IntegerField(
        write_only=True, allow_null=True, required=False
    )
    agent = PersonSerializer(read_only=True)
    agent_id = serializers.IntegerField(
        write_only=True, allow_null=True, required=False
    )
    is_on_lease = TextChoiceField(LeaseType, required=False)
    rental_circumstances = TextChoiceField(RentalType, required=False)
    started = serializers.DateTimeField(
        format="%d/%m/%Y", input_formats=["%d/%m/%Y"], required=False
    )
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        return reverse("tenancy-detail", args=(obj.pk,))
