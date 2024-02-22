from rest_framework import serializers
from django.urls import reverse

from core.models import Client
from core.models.client import (
    CallTime,
    EligibilityCircumstanceType,
    AboriginalOrTorresStraitIslander,
    RequiresInterpreter,
)
from .fields import TextChoiceField, TextChoiceListField


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = (
            "id",
            "first_name",
            "last_name",
            "preferred_name",
            "email",
            "date_of_birth",
            "phone_number",
            "gender",
            "pronouns",
            "centrelink_support",
            "eligibility_notes",
            "requires_interpreter",
            "primary_language_non_english",
            "primary_language",
            "is_aboriginal_or_torres_strait_islander",
            "number_of_dependents",
            "eligibility_circumstances",
            "age",
            "full_name",
            "notes",
            "call_times",
            "url",
        )

    id = serializers.CharField(read_only=True)
    age = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    date_of_birth = serializers.DateTimeField(
        format="%d/%m/%Y", input_formats=["%d/%m/%Y"]
    )
    call_times = TextChoiceListField(CallTime)
    eligibility_circumstances = TextChoiceListField(EligibilityCircumstanceType)
    is_aboriginal_or_torres_strait_islander = TextChoiceField(
        AboriginalOrTorresStraitIslander
    )
    requires_interpreter = TextChoiceField(RequiresInterpreter)

    def get_url(self, obj):
        return reverse("client-detail", args=(obj.pk,))

    def get_age(self, obj):
        return obj.get_age()

    def get_full_name(self, obj):
        return obj.get_full_name()
