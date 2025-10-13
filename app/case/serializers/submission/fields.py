from rest_framework import serializers


class StringOrListField(serializers.ListField):
    """A field that can accept either a string or a list of strings."""

    def to_representation(self, data):
        if data is not None:
            if not isinstance(data, list):
                data = [data]
            data = [item for item in data if item is not None]
        return super().to_representation(data)
