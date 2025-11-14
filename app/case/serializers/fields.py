from django.utils import timezone
from rest_framework import serializers


class BooleanYesNoDisplayField(serializers.BooleanField):
    def to_representation(self, value):  # pyright: ignore [reportIncompatibleMethodOverride]
        value = super().to_representation(value)
        if value is True:
            return {"label": "Yes", "value": True}
        else:
            return {"label": "No", "value": False}

    def to_internal_value(self, data):
        return super().to_internal_value(data.get("value"))


class ChoiceDisplayField(serializers.ChoiceField):
    def to_representation(self, value):
        value = super().to_representation(value)
        label = self.choices.get(value)
        return {"label": label, "value": value}

    def to_internal_value(self, data):
        return super().to_internal_value(data.get("value"))


class TextChoiceField(serializers.CharField):
    def __init__(self, text_choice_cls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text_choice_cls = text_choice_cls

    def to_representation(self, value):  # pyright: ignore [reportIncompatibleMethodOverride]
        display = self.text_choice_cls[value].label if value else ""
        choices = self.text_choice_cls.choices
        if self.allow_blank:
            choices.insert(0, ("", "-"))
        return {
            "display": display,
            "value": value,
            "choices": choices,
        }


class TextChoiceListField(serializers.ListField):
    child = serializers.CharField()

    def __init__(self, text_choice_cls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text_choice_cls = text_choice_cls

    def to_representation(self, value):  # pyright: ignore [reportIncompatibleMethodOverride]
        display = " | ".join(self.text_choice_cls[s].label for s in value if s)
        return {
            "display": display,
            "value": [v for v in value if v],
            "choices": self.text_choice_cls.choices,
        }


class DateField(serializers.ReadOnlyField):
    def to_representation(self, value):
        if not value:
            return None
        else:
            return value.strftime("%d/%m/%y")


class LocalDateField(serializers.ReadOnlyField):
    def to_representation(self, value):
        if not value:
            return None
        else:
            return timezone.localtime(value).strftime("%d/%m/%y")


class LocalTimeField(serializers.ReadOnlyField):
    def to_representation(self, value):
        if not value:
            return None
        else:
            return timezone.localtime(value).strftime("%d/%m/%y at %-I%p")
