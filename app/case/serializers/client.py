from core.models import Client
from core.models.client import (
    AboriginalOrTorresStraitIslander,
    CallTime,
    ContactRestriction,
    EligibilityCircumstanceType,
    RequiresInterpreter,
)
from django.urls import reverse
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .fields import TextChoiceField, TextChoiceListField


class ClientSearchSerializer(serializers.Serializer):
    q = serializers.CharField(max_length=256, required=True)


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
            "contact_restriction",
            "contact_notes",
            "age",
            "full_name",
            "notes",
            "call_times",
            "url",
        )

    id = serializers.CharField(read_only=True)
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=Client.objects.all())], required=True
    )
    date_of_birth = serializers.DateTimeField(
        format="%d/%m/%Y", input_formats=["%d/%m/%Y"], required=False
    )
    call_times = TextChoiceListField(CallTime, required=False)
    eligibility_circumstances = TextChoiceListField(
        EligibilityCircumstanceType, required=False
    )
    is_aboriginal_or_torres_strait_islander = TextChoiceField(
        AboriginalOrTorresStraitIslander, required=False
    )
    full_name = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    requires_interpreter = TextChoiceField(RequiresInterpreter, required=False)
    contact_restriction = TextChoiceField(
        ContactRestriction, required=False, allow_blank=True
    )

    def get_url(self, obj):
        return reverse("client-detail", args=(obj.pk,))

    def get_age(self, obj):
        return obj.get_age()

    def get_full_name(self, obj):
        return obj.get_full_name()
