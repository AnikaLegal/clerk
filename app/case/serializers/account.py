from rest_framework import serializers
from accounts.models import User


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