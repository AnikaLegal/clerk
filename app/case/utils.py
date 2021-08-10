from django.forms import ModelForm, SelectMultiple, Select
from django.forms.fields import ChoiceField
from django.template.loader import render_to_string
from django.shortcuts import render
from django.http import Http404
from django.contrib import messages
from django.contrib.postgres.forms.array import SimpleArrayField

DYNAMIC_FORM_TEMPLATE = "case/snippets/_dynamic_form.html"


class FomanticSelect(Select):
    template_name = "case/snippets/_dropdown_widget.html"

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        options = []
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
    template_name = "case/snippets/_dropdown_widget.html"

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        selected_options = value.split(",")
        options = []
        for choice_val, choice_label in self.attrs["choices"]:
            option = {
                "name": choice_label,
                "value": choice_val,
                "selected": choice_val in selected_options,
            }
            options.append(option)

        context["options"] = options
        return context


class SingleChoiceField(ChoiceField):
    widget = FomanticSelect

    def __init__(self, field_name, model):
        self.choices = getattr(model, field_name).field.choices
        self.choice_map = {v: l for v, l in self.choices}
        super().__init__(choices=self.choices)

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


class DynamicModelForm(ModelForm):
    def __init__(self, slug: str, *args, editable: bool = False, **kwargs):
        super().__init__(*args, **kwargs)
        self.editable = editable
        self.slug = slug

        # Build display value for fields
        for bound_field in self:
            if hasattr(bound_field.field, "display_value"):
                bound_field.display_value = bound_field.field.display_value(bound_field)
            else:
                bound_field.display_value = bound_field.value()

    def render_to_string(self):
        context = {"form": self}
        return render_to_string(DYNAMIC_FORM_TEMPLATE, context)

    def render_to_response(self, request, context):
        context = {**context, "form": self}
        return render(request, DYNAMIC_FORM_TEMPLATE, context)

    def __str__(self):
        return self.render_to_string()

    @staticmethod
    def build_forms(request, slug: str, instance, view_forms: dict) -> dict:
        form_instances = {}
        for form_slug, form_cls in view_forms.items():
            form_kwargs = dict(instance=instance, slug=form_slug, editable=False)
            if request.method == "POST" and form_slug == slug:
                form_kwargs["data"] = request.POST

            form_instances[form_slug] = form_cls(**form_kwargs)

        return form_instances

    @staticmethod
    def get_response(request, slug: str, forms: dict, context: dict):
        if not slug:
            return

        form = forms.get(slug)
        if not form:
            raise Http404()

        ctx = {**context, "slug": slug}
        if request.method == "GET":
            is_editable = request.GET.get("edit")
            form.editable = is_editable
            return form.render_to_response(request, ctx)
        elif request.method == "POST":
            if form.is_valid():
                form.save()
                messages.success(request, "Edit success")
            else:
                form.editable = True

            return form.render_to_response(request, ctx)
        else:
            raise Http404()
