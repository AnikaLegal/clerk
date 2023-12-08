from rest_framework import serializers
from django.urls import reverse

from core.models.tenancy import Tenancy, LeaseType
from .client import ClientSerializer
from .person import PersonSerializer
from .fields import DateField, TextChoiceField


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
            "landlord",
            "agent",
            "client",
            "url",
        )

    client = ClientSerializer(read_only=True)
    landlord = PersonSerializer(read_only=True)
    agent = PersonSerializer(read_only=True)
    url = serializers.SerializerMethodField()
    is_on_lease = TextChoiceField(LeaseType, allow_blank=True)
    started = serializers.DateTimeField(format="%d/%m/%Y", input_formats=["%d/%m/%Y"])

    def get_url(self, obj):
        return reverse("tenancy-detail", args=(obj.pk,))
