from django.forms import SelectMultiple, Select


class FomanticSelect(Select):
    template_name = "case/forms/_dropdown_widget.html"

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        options = []
        # Assume field has set an attribute via `widget_attrs` method.
        for choice_val, choice_label in self.attrs["choices"]:
            option = {
                "name": choice_label,
                "value": choice_val,
                "selected": choice_val == value,
            }
            options.append(option)

        context["options"] = options
        return context


class FomanticSelectMultiple(SelectMultiple):
    template_name = "case/forms/_dropdown_widget.html"

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        selected_options = value.split(",")
        options = []
        # Assume field has set an attribute via `widget_attrs` method.
        for choice_val, choice_label in self.attrs["choices"]:
            option = {
                "name": choice_label,
                "value": choice_val,
                "selected": choice_val in selected_options,
            }
            options.append(option)

        context["options"] = options
        return context