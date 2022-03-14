from django.forms import ModelForm
from django.template.loader import render_to_string
from django.shortcuts import render
from django.http import Http404
from django.contrib import messages


class DynamicTableForm(ModelForm):
    """
    Renders a table which can be optionally edited by a user using htmx.
    Updates the provided instance when the form is submitted.
    Suggested usage within a view:

        DYNAMIC_FORMS = {
            "foo": BarForm,
            "bar": FooForm,
        }

        def thing_view(request, pk, form_slug: str = ""):
            # ...
            forms = DynamicTableForm.build_forms(request, form_slug, client, DYNAMIC_FORMS)
            context = {"whatever": 1, "forms": forms}
            form_resp = DynamicTableForm.get_response(request, form_slug, forms, context)
            if form_resp:
                return form_resp
            # ...

    Needs to be hooked up in urls.py as follows:

        urlpatterns = [
            # ...

            # Thing
            path("thing/<int:pk>/", views.thing.thing_view, name="thing-detail"),
            path(
                "thing/<int:pk>/<str:form_slug>/",
                views.thing.thing_view,
                name="thing-detail-form",
            ),
            # ...
        ]

    """

    template = "case/forms/_dynamic_table_form.html"
    not_required_fields = []

    def __init__(self, slug: str, *args, editable: bool = False, **kwargs):
        super().__init__(*args, **kwargs)
        self.editable = editable
        self.slug = slug
        self.set_display_values()
        for fname in self.not_required_fields:
            self.fields[fname].required = False

    def set_display_values(self):
        # Build display value for fields
        for bound_field in self:
            if hasattr(bound_field.field, "display_value"):
                bound_field.display_value = bound_field.field.display_value(bound_field)
            else:
                bound_field.display_value = bound_field.value()

    def render_to_string(self):
        context = {"form": self}
        return render_to_string(self.template, context)

    def render_to_response(self, request, context):
        context = {**context, "form": self}
        return render(request, self.template, context)

    def __str__(self):
        return self.render_to_string()

    @staticmethod
    def build_forms(
        request, slug: str, instance, view_forms: dict, extra_kwargs: dict = None
    ) -> dict:
        form_instances = {}
        for form_slug, form_cls in view_forms.items():
            # Get default kwargs for this form
            form_kwargs = dict(instance=instance, slug=form_slug, editable=False)
            # If the POST request is for this particular form, add that in too.
            if request.method == "POST" and form_slug == slug:
                form_kwargs["data"] = request.POST
            # Add in any custom kwargs
            if extra_kwargs:
                _extra_kwargs = extra_kwargs.get(form_slug)
                if _extra_kwargs:
                    form_kwargs = {**form_kwargs, **_extra_kwargs}

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
