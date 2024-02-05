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

    landlord = PersonSerializer(read_only=True)
    agent = PersonSerializer(read_only=True)
    landlord_id = serializers.IntegerField(write_only=True, allow_null=True)
    agent_id = serializers.IntegerField(write_only=True, allow_null=True)
    url = serializers.SerializerMethodField()
    is_on_lease = TextChoiceField(LeaseType, allow_blank=True)
    rental_circumstances = TextChoiceField(RentalType)
    started = serializers.DateTimeField(format="%d/%m/%Y", input_formats=["%d/%m/%Y"])

    def get_url(self, obj):
        return reverse("tenancy-detail", args=(obj.pk,))
