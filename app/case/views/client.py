from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.http import Http404


from case.forms import (
    DynamicModelForm,
    ClientContactDynamicForm,
    ClientMiscDynamicForm,
    ClientPersonalDynamicForm,
    TenancyDynamicForm,
    PersonDynamicForm,
)
from core.models import Client, Tenancy, Person

from django.contrib.auth.decorators import user_passes_test
from .auth import is_superuser

CLIENT_DETAIL_FORMS = {
    "contact": ClientContactDynamicForm,
    "personal": ClientPersonalDynamicForm,
    "misc": ClientMiscDynamicForm,
}

TENANCY_DETAIL_FORMS = {
    "form": TenancyDynamicForm,
}

PERSON_DETAIL_FORMS = {
    "form": PersonDynamicForm,
}


# FIXME: Permissions
@login_required
@user_passes_test(is_superuser, login_url="/")
@require_http_methods(["GET", "POST"])
def client_detail_view(request, pk, form_slug: str = ""):
    try:
        # FIXME: Who has access to this?
        client = Client.objects.prefetch_related("issue_set").get(pk=pk)
    except Client.DoesNotExist:
        raise Http404()

    forms = DynamicModelForm.build_forms(
        request, form_slug, client, CLIENT_DETAIL_FORMS
    )
    context = {"client": client, "forms": forms}
    form_resp = DynamicModelForm.get_response(request, form_slug, forms, context)
    if form_resp:
        return form_resp
    else:
        return render(request, "case/client_detail.html", context)


# FIXME: Permissions
@login_required
@user_passes_test(is_superuser, login_url="/")
@require_http_methods(["GET", "POST"])
def tenancy_detail_view(request, pk, form_slug: str = ""):
    try:
        # FIXME: Who has access to this?
        tenancy = Tenancy.objects.get(pk=pk)
    except Tenancy.DoesNotExist:
        raise Http404()

    forms = DynamicModelForm.build_forms(
        request, form_slug, tenancy, TENANCY_DETAIL_FORMS
    )
    context = {"tenancy": tenancy, "forms": forms}
    form_resp = DynamicModelForm.get_response(request, form_slug, forms, context)
    if form_resp:
        return form_resp
    else:
        return render(request, "case/tenancy_detail.html", context)


# FIXME: Permissions
@login_required
@user_passes_test(is_superuser, login_url="/")
@require_http_methods(["GET", "POST"])
def person_detail_view(request, pk, form_slug: str = ""):
    try:
        # FIXME: Who has access to this?
        person = Person.objects.get(pk=pk)
    except Person.DoesNotExist:
        raise Http404()

    forms = DynamicModelForm.build_forms(
        request, form_slug, person, PERSON_DETAIL_FORMS
    )
    context = {"person": person, "forms": forms}
    form_resp = DynamicModelForm.get_response(request, form_slug, forms, context)
    if form_resp:
        return form_resp
    else:
        return render(request, "case/person_detail.html", context)
