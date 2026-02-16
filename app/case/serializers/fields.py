from django.utils import timezone
from rest_framework import serializers
from rest_framework.relations import MANY_RELATION_KWARGS


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


class SlugRelatedTextChoiceField(serializers.SlugRelatedField):
    class CustomManyRelatedField(serializers.ManyRelatedField):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._choices_list = None

        @property
        def choices_list(self):
            if self._choices_list is None:
                self._choices_list = [list(pair) for pair in self.choices.items()]
            return self._choices_list

        def to_representation(self, iterable):  # pyright: ignore [reportIncompatibleMethodOverride]
            iterable = super().to_representation(iterable)
            # NOTE: the display and value are the same as they are the value of
            # the related field.
            return {
                "display": " | ".join(iterable),
                "value": iterable,
                "choices": self.choices_list,
            }

    @classmethod
    def many_init(cls, *args, **kwargs):
        list_kwargs = {"child_relation": cls(*args, **kwargs)}
        for key in kwargs:
            if key in MANY_RELATION_KWARGS:
                list_kwargs[key] = kwargs[key]
        return cls.CustomManyRelatedField(**list_kwargs)


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
