from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.http import Http404
from django.contrib import messages


from case.forms import ClientContactDynamicForm
from core.models import Client

from django.contrib.auth.decorators import user_passes_test
from .auth import is_superuser

CLIENT_DETAIL_FORMS = {
    "contact": ClientContactDynamicForm,
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

    client_info = [
        {"label": "Email", "value": client.email},
        {"label": "Phone number", "value": client.phone_number},
        {
            "label": "Preferred call times",
            "value": client.call_times,
        },
        {"label": "Date of birth", "value": client.date_of_birth},
        {"label": "Gender", "value": client.gender},
        {"label": "Employment Status", "value": client.employment_status},
        {
            "label": "Special Circumstances",
            "value": client.special_circumstances,
        },
        {"label": "Weekly Income", "value": client.weekly_income},
        {"label": "Weekly Rent", "value": client.weekly_rent},
        {
            "label": "Primary language non-english",
            "value": client.primary_language_non_english,
        },
        {"label": "Primary language", "value": client.primary_language},
        {"label": "Rental circumstanbces", "value": client.rental_circumstances},
        {
            "label": "Is multi income household",
            "value": client.is_multi_income_household,
        },
        {"label": "Number of dependents", "value": client.number_of_dependents},
        {
            "label": "Is Aboriginal or Torres Strait Islander",
            "value": client.is_aboriginal_or_torres_strait_islander,
        },
        {"label": "Referrer Type", "value": client.referrer_type},
        {"label": "Referrer", "value": client.referrer},
        {
            "label": "Legal access difficulties",
            "value": client.legal_access_difficulties,
        },
    ]
    client_info = (fmt(i) for i in client_info)
    client_info = (i for i in client_info if i["value"])
    form = ClientContactDynamicForm(instance=client, slug="contact", editable=False)
    context = {"client": client, "client_info": client_info, "form": form}

    form_cls = None
    if form_slug:
        form_cls = CLIENT_DETAIL_FORMS.get(form_slug)
        if not form_cls:
            raise Http404()

        context = {**context, "slug": form_slug}
        if request.method == "GET":
            is_editable = request.GET.get("edit")
            form.editable = is_editable
            return form.render_to_response(request, context)
        elif request.method == "POST":
            if form.is_valid():
                form.save()
                messages.success(request, "Edit success")
            else:
                form.editable = True

            return form.render_to_response(request, context)
        else:
            raise Http404()
    else:
        return render(request, "case/client_detail.html", context)


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