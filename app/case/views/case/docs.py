from django.http import Http404
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from microsoft.service import get_files_for_case
from case.views.auth import paralegal_or_better_required
from case.utils.router import Route
from core.models import Issue

from .detail import _get_actionstep_url

MAYBE_IMAGE_FILE_EXTENSIONS = [".png", ".jpg", ".jpeg"]

docs_route = Route("docs").uuid("pk").path("docs")


@docs_route
@paralegal_or_better_required
@require_http_methods(["GET", "POST"])
def case_detail_documents_view(request, pk):
    """
    The documents of a given case.
    """
    try:
        issue_qs = Issue.objects.select_related("client")
        if request.user.is_paralegal:
            # Paralegals can only see cases that they are assigned to
            issue_qs.filter(paralegal=request.user)

        issue = issue_qs.get(pk=pk)
    except Issue.DoesNotExist:
        raise Http404()

    documents = get_files_for_case(issue)

    context = {
        "issue": issue,
        "actionstep_url": _get_actionstep_url(issue),
        "documents": documents,
    }
    return render(request, "case/docs_list.html", context)


MAYBE_IMAGE_FILE_EXTENSIONS = [".png", ".jpg", ".jpeg"]
