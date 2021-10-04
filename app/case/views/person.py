from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.http import Http404

from case.forms import DynamicTableForm, PersonDynamicForm
from core.models import Person
from .auth import paralegal_or_better_required
from case.utils.router import Router

PERSON_DETAIL_FORMS = {
    "form": PersonDynamicForm,
}

router = Router("person")
router.create_route("detail").pk("pk").slug("form_slug", optional=True)


@router.use_route("detail")
@paralegal_or_better_required
@require_http_methods(["GET", "POST"])
def person_detail_view(request, pk, form_slug: str = ""):
    try:
        # FIXME: Limit access to only paralegals who are assigned to cases where
        # There people are involved.
        person = Person.objects.get(pk=pk)
    except Person.DoesNotExist:
        raise Http404()

    forms = DynamicTableForm.build_forms(
        request, form_slug, person, PERSON_DETAIL_FORMS
    )
    context = {"person": person, "forms": forms}
    form_resp = DynamicTableForm.get_response(request, form_slug, forms, context)
    if form_resp:
        return form_resp
    else:
        return render(request, "case/person_detail.html", context)
