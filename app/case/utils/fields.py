from django.forms.fields import ChoiceField
from django.contrib.postgres.forms.array import SimpleArrayField

from .widgets import FomanticSelect, FomanticSelectMultiple


class SingleChoiceField(ChoiceField):
    widget = FomanticSelect

    def __init__(self, field_name=None, model=None, choices=None, **kwargs):
        if field_name and model:
            self.choices = getattr(model, field_name).field.choices
        elif choices:
            self.choices = choices

        self.choice_map = {v: l for v, l in self.choices}
        super().__init__(choices=self.choices, **kwargs)

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        attrs["choices"] = self.choices
        return attrs

    def display_value(self, bound_field):
        val = bound_field.value()
        return self.choice_map.get(val, "-")


class MultiChoiceField(SimpleArrayField):
    widget = FomanticSelectMultiple

    def __init__(self, field_name, model):
        self.choices = getattr(model, field_name).field.base_field.choices
        self.choice_map = {v: l for v, l in self.choices}
        super().__init__(ChoiceField(choices=self.choices))

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        attrs["choices"] = self.choices
        return attrs

    def display_value(self, bound_field):
        vals = bound_field.value().split(",")
        display_vals = [self.choice_map.get(v, "-") for v in vals]
        return " | ".join(display_vals)
