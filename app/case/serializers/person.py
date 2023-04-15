from rest_framework import serializers
from django.urls import reverse

from core.models import Person
from core.models.person import SupportContactPreferences
from .fields import TextChoiceField


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ("id", "full_name", "email", "address", "phone_number", "url")

    url = serializers.SerializerMethodField()
    support_contact_preferences = TextChoiceField(SupportContactPreferences)

    def get_url(self, obj):
        return reverse("person-detail", args=(obj.pk,))
