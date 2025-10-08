from rest_framework import serializers


class StringOrListField(serializers.ListField):
    """A field that can accept either a string or a list of strings."""

    def to_representation(self, data):
        if data is not None and not isinstance(data, list):
            data = [data]
        return super().to_representation(data)
