from django.forms import ModelForm
from django.template.loader import render_to_string
from django.shortcuts import render

DYNAMIC_FORM_TEMPLATE = "case/snippets/_dynamic_form.html"


class DynamicModelForm(ModelForm):
    def __init__(self, slug: str, *args, editable: bool = False, **kwargs):
        super().__init__(*args, **kwargs)
        self.editable = editable
        self.slug = slug

    def render_to_string(self):
        context = {"form": self}
        return render_to_string(DYNAMIC_FORM_TEMPLATE, context)

    def render_to_response(self, request, context):
        context = {**context, "form": self}
        return render(request, DYNAMIC_FORM_TEMPLATE, context)

    def __str__(self):
        return self.render_to_string()

    @classmethod
    def get_response(cls):
        pass