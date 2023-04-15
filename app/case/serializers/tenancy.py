from rest_framework import serializers
from django.urls import reverse

from core.models import Tenancy

from .person import PersonSerializer
from .fields import DateField


class TenancySerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenancy
        fields = (
            "address",
            "suburb",
            "postcode",
            "started",
            "is_on_lease",
            "landlord",
            "agent",
            "url",
        )

    landlord = PersonSerializer(read_only=True)
    agent = PersonSerializer(read_only=True)
    url = serializers.SerializerMethodField()
    is_on_lease = serializers.CharField(source="get_is_on_lease_display")
    started = DateField()

    def get_url(self, obj):
        return reverse("tenancy-detail", args=(obj.pk,))
