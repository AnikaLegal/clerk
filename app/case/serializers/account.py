from rest_framework import serializers
from accounts.models import User

SORT_CHOICES = [
    "case_capacity",
    "date_joined",
    "email",
    "first_name",
    "last_name",
]
# Add descending sort choices.
SORT_CHOICES.extend([f"-{x}" for x in SORT_CHOICES])


class AccountSortSerializer(serializers.Serializer):
    class Meta:
        fields = ("sort",)

    sort = serializers.MultipleChoiceField(choices=SORT_CHOICES, required=False)


class AccountSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "is_active",
            "name",
            "group",
        )
        extra_kwargs = {f: {"required": False} for f in fields}

    name = serializers.CharField(required=False)
    group = serializers.CharField(required=False)
