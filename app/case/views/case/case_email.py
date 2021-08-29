from django.http import Http404
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from core.models import Issue
from case.views.auth import paralegal_or_better_required


@paralegal_or_better_required
@require_http_methods(["GET", "POST"])
def case_detail_email_view(request, pk, form_slug=""):
    try:
        issue = Issue.objects.check_permisisons(request).get(pk=pk)
    except Issue.DoesNotExist:
        raise Http404()

    if form_slug == "draft":
        pass
    elif form_slug == "email":
        pass

    context = {"issue": issue}
    return render(request, "case/case_detail_email.html", context)
