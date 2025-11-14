from rest_framework import serializers
import os


class FileUploadField(serializers.DictField):
    """A field for handling file uploads represented as a dictionary."""

    def to_representation(self, value):
        file = value.get("file")
        basename = os.path.basename(file) if file else None

        return super().to_representation(
            {
                "name": basename,
                "url": file,
            }
        )


class StringOrListField(serializers.ListField):
    """A field that can accept either a string or a list of strings."""

    def to_representation(self, data):
        if data is not None:
            if not isinstance(data, list):
                data = [data]
            data = [item for item in data if item is not None]
        return super().to_representation(data)


class TidyJsonField(serializers.JSONField):
    """A JSON field that sorts its keys and removes null values in its representation."""

    def to_representation(self, value):
        # recursively sort and remove null values from representation.
        def tidy(value):
            if isinstance(value, dict):
                return dict(
                    sorted((k, tidy(v)) for k, v in value.items() if v is not None)
                )
            elif isinstance(value, list):
                return [tidy(v) for v in value if v is not None]
            return value

        value = tidy(value)
        return super().to_representation(value)
