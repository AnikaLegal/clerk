from django.http import Http404
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from microsoft.service import get_docs_info_for_case
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
        issue = (
            Issue.objects.check_permisisons(request).select_related("client").get(pk=pk)
        )
    except Issue.DoesNotExist:
        raise Http404()

    documents, sharepoint_url, sharing_url = get_docs_info_for_case(issue, request.user)
    context = {
        "issue": issue,
        "actionstep_url": _get_actionstep_url(issue),
        "sharepoint_url": sharepoint_url,
        "sharing_url": sharing_url,
        "documents": documents,
    }
    return render(request, "case/docs_list.html", context)


MAYBE_IMAGE_FILE_EXTENSIONS = [".png", ".jpg", ".jpeg"]
