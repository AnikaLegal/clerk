from rest_framework import serializers
from django.urls import reverse

from core.models import Person
from core.models.person import SupportContactPreferences
from .fields import TextChoiceField


class PersonSearchRequestSerializer(serializers.Serializer):
    query = serializers.CharField(max_length=256, required=False, allow_blank=True)


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = (
            "id",
            "full_name",
            "email",
            "address",
            "phone_number",
            "url",
            "support_contact_preferences",
        )

    url = serializers.SerializerMethodField()
    support_contact_preferences = TextChoiceField(
        SupportContactPreferences, allow_blank=True
    )

    def get_url(self, obj):
        return reverse("person-detail", args=(obj.pk,))
