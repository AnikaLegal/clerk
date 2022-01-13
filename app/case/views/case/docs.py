from django.http import Http404
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from microsoft.service import get_case_folder_info
from case.views.auth import paralegal_or_better_required
from case.utils.router import Route
from core.models import Issue

from .detail import _get_actionstep_url


docs_route = Route("docs").uuid("pk").path("docs")
docs_sharepoint_route = (
    Route("docs-sharepoint").uuid("pk").path("docs").path("sharepoint")
)


@docs_route
@paralegal_or_better_required
@require_http_methods(["GET", "POST"])
def case_detail_documents_view(request, pk):
    """
    The documents of a given case.
    """
    try:
        issue = (
            Issue.objects.check_permissions(request).select_related("client").get(pk=pk)
        )
    except Issue.DoesNotExist:
        raise Http404()

    context = {
        "issue": issue,
        "actionstep_url": _get_actionstep_url(issue),
        "is_loading": True,
    }
    return render(request, "case/docs/list.html", context)


@docs_sharepoint_route
@paralegal_or_better_required
@require_http_methods(["GET", "POST"])
def sharepoint_docs_view(request, pk):
    try:
        issue = (
            Issue.objects.check_permissions(request).select_related("client").get(pk=pk)
        )
    except Issue.DoesNotExist:
        raise Http404()

    documents, sharepoint_url = get_case_folder_info(issue)
    context = {
        "is_loading": False,
        "sharepoint_url": sharepoint_url,
        "documents": documents,
    }
    return render(request, "case/docs/_sharepoint.html", context)
