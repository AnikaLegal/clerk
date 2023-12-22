from django.db.models import Max
from rest_framework.decorators import api_view

from case.serializers import IssueSerializer
from core.models import Issue, IssueNote
from case.utils.react import render_react_page
from case.views.auth import (
    coordinator_or_better_required,
)


@api_view(["GET"])
@coordinator_or_better_required
def case_review_page_view(request):
    """Page where coordinators can see existing cases for them to review"""
    issues = (
        Issue.objects.select_related("client")
        .prefetch_related("issuenote_set", "paralegal__groups", "lawyer__groups")
        .filter(is_open=True)
        .annotate(next_review=Max("issuenote__event"))
        .order_by("next_review")
    )
    issues = IssueNote.annotate_with_eligibility_checks(issues)
    context = {"issues": IssueSerializer(issues, many=True).data}
    return render_react_page(request, "Case Review", "case-review", context)
