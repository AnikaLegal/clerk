from django.db.models import Q
from rest_framework.decorators import api_view

from case.serializers import IssueSerializer
from core.models import Issue, IssueNote
from case.utils.react import render_react_page
from case.views.auth import (
    coordinator_or_better_required,
)


@api_view(["GET"])
@coordinator_or_better_required
def case_inbox_page_view(request):
    """Inbox page where coordinators can see new cases for them to assign"""
    is_unassigned = Q(paralegal__isnull=True)
    is_open = Q(is_open=True)
    is_inbox = is_unassigned & is_open
    issues = (
        Issue.objects.select_related("client")
        .prefetch_related("issuenote_set", "paralegal__groups", "lawyer__groups")
        .filter(is_inbox)
        .order_by("created_at")
    )
    issues = IssueNote.annotate_with_eligibility_checks(issues)
    context = {"issues": IssueSerializer(issues, many=True).data}
    return render_react_page(request, "Case Inbox", "case-inbox", context)
