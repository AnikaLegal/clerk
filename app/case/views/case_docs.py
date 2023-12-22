from django.http import Http404

from microsoft.service import get_case_folder_info
from case.views.auth import paralegal_or_better_required
from core.models import Issue
from case.utils.react import render_react_page
from case.views.case_detail import get_detail_urls
from case.serializers import IssueSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["GET"])
@paralegal_or_better_required
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
        "issue": IssueSerializer(issue).data,
        "urls": get_detail_urls(issue),
    }
    return render_react_page(request, f"Case {issue.fileref}", "document-list", context)


@api_view(["GET"])
@paralegal_or_better_required
def sharepoint_docs_view(request, pk):
    try:
        issue = (
            Issue.objects.check_permissions(request).select_related("client").get(pk=pk)
        )
    except Issue.DoesNotExist:
        raise Http404()

    documents, sharepoint_url = get_case_folder_info(issue)
    data = {"sharepoint_url": sharepoint_url, "documents": documents}
    return Response(data)
