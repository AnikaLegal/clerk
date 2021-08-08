from django.forms import ModelForm, SelectMultiple
from django.template.loader import render_to_string
from django.shortcuts import render
from django.http import Http404
from django.contrib import messages
from django.contrib.postgres.forms.array import SimpleArrayField

DYNAMIC_FORM_TEMPLATE = "case/snippets/_dynamic_form.html"


class DynamicModelForm(ModelForm):
    def __init__(self, slug: str, *args, editable: bool = False, **kwargs):
        super().__init__(*args, **kwargs)
        self.editable = editable
        self.slug = slug
        for field in self.fields.values():
            if type(field) is SimpleArrayField:
                base_widget = field.base_field.widget
                if getattr(base_widget, "choices", None):
                    # Multiple pre-defined choices.
                    attrs = {**base_widget.attrs, "class": "ui dropdown"}
                    field.widget = FomanticSelectMultiple(attrs, base_widget.choices)

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


class FomanticSelectMultiple(SelectMultiple):
    template_name = "case/snippets/_dropdown_widget.html"

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        selected_options = value.split(",")
        options = []
        for _, group_choices, _ in context["widget"]["optgroups"]:
            for choice in group_choices:
                if choice["value"]:
                    option = {
                        "name": choice["label"],
                        "value": choice["value"],
                        "selected": choice["value"] in selected_options,
                    }
                    options.append(option)

        context["options"] = options
        return context


# DEAD CODE
def fmt(item):
    v = item["value"]
    if type(v) is list:
        v = ", ".join([el.capitalize().replace("_", " ") for el in v if el])
    elif type(v) is str:
        v = v.capitalize().replace("_", " ")
        if "@" in v:
            v = v.lower()

    item["value"] = v
    return {**item, "value": v}