from rest_framework import serializers


class NoEmailSerializer(serializers.Serializer):
    name = serializers.CharField(min_length=2)
    phone_number = serializers.CharField(min_length=6)