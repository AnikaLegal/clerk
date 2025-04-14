from rest_framework import serializers
from django.utils import timezone


class TextChoiceField(serializers.CharField):
    def __init__(self, text_choice_cls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text_choice_cls = text_choice_cls

    def to_representation(self, value):
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

    def to_representation(self, value):
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
