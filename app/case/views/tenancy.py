from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.http import Http404


from case.forms import DynamicTableForm, TenancyDynamicForm
from core.models import Tenancy, Issue
from .auth import paralegal_or_better_required

TENANCY_DETAIL_FORMS = {
    "form": TenancyDynamicForm,
}


@paralegal_or_better_required
@require_http_methods(["GET", "POST"])
def tenancy_detail_view(request, pk, form_slug: str = ""):
    try:
        tenancy = Tenancy.objects.get(pk=pk)
        if request.user.is_paralegal:
            is_assigned = Issue.objects.filter(
                client=tenancy.client, paralegal=request.user
            ).exists()
            if not is_assigned:
                # Not allowed
                raise Http404()

    except Tenancy.DoesNotExist:
        raise Http404()

    forms = DynamicTableForm.build_forms(
        request, form_slug, tenancy, TENANCY_DETAIL_FORMS
    )
    context = {"tenancy": tenancy, "forms": forms}
    form_resp = DynamicTableForm.get_response(request, form_slug, forms, context)
    if form_resp:
        return form_resp
    else:
        return render(request, "case/tenancy_detail.html", context)
