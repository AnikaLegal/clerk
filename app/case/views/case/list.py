from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Max, Exists, OuterRef
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response

from core.models import Issue
from core.models.issue_note import NoteType, IssueNote
from core.models.issue import CaseStage, CaseOutcome, CaseTopic
from case.forms import IssueSearchForm, LawyerFilterForm
from case.utils import get_page
from case.utils.react import render_react_page, is_react_api_call
from case.views.auth import coordinator_or_better_required
from case.utils.router import Route

from case.serializers import IssueDetailSerializer

COORDINATORS_EMAIL = "coordinators@anikalegal.com"

list_route = Route("list")
inbox_route = Route("inbox").path("inbox")
review_search_route = Route("review-search").path("review").path("search")
review_route = Route("review").path("review")
checks_route = Route("checks").path("checks")


@list_route
@login_required
@api_view(["GET"])
def case_list_view(request):
    """
    List of all cases for paralegals and coordinators to view.
    """
    issue_qs = _get_issue_qs_for_user(request.user)
    form = IssueSearchForm(request.GET)
    issue_qs = form.search(issue_qs).order_by("-created_at").all()
    page, next_page, prev_page = get_page(
        request, issue_qs, per_page=14, return_qs=False
    )
    context = {
        "issues": IssueDetailSerializer(page.object_list, many=True).data,
        "next_page": next_page,
        "total_pages": page.paginator.num_pages,
        "total_count": page.paginator.count,
        "prev_page": prev_page,
        "choices": {
            "stage": CaseStage.CHOICES,
            "topic": CaseTopic.CHOICES,
            "outcome": CaseOutcome.CHOICES,
            "is_open": [
                ("True", "Open"),
                ("False", "Closed"),
            ],
        },
    }
    if is_react_api_call(request):
        return Response(context)
    else:
        return render_react_page(request, f"Cases", "case-list", context)


def _get_issue_qs_for_user(user):
    issue_qs = Issue.objects.select_related("client").prefetch_related(
        "paralegal__groups", "lawyer__groups"
    )
    if user.is_paralegal:
        # Paralegals can only see assigned cases
        issue_qs = issue_qs.filter(paralegal=user)
    elif not user.is_coordinator_or_better:
        # If you're not a paralegal or coordinator you can't see nuthin.
        issue_qs = issue_qs.none()

    return issue_qs


@review_route
@coordinator_or_better_required
@require_http_methods(["GET"])
def case_review_view(request):
    """Page where coordinators can see existing cases for them to review"""
    issues = _get_review_issue_qs()
    _annotate_issue_review_color(issues)
    alert_issues = [
        i
        for i in issues
        if i.stage != CaseStage.UNSTARTED
        and not (i.is_conflict_check and i.is_eligibility_check)
    ]
    form = LawyerFilterForm()
    context = {"issues": issues, "alert_issues": alert_issues, "form": form}
    return render(request, "case/case/review.html", context)


@review_search_route
@coordinator_or_better_required
@require_http_methods(["GET"])
def case_review_search_view(request):
    """Page where coordinators can see existing cases for them to review"""
    issues = _get_review_issue_qs()
    _annotate_issue_review_color(issues)
    form = LawyerFilterForm(request.GET)
    if form.is_valid():
        lawyer = form.cleaned_data["lawyer"]
        if lawyer:
            issues = issues.filter(lawyer=lawyer)

    context = {
        "issues": issues,
        "table_id": "review-table",
        "is_review": True,
        "is_open": True,
    }
    return render(request, "case/case/_list_table.html", context)


def _get_review_issue_qs():
    issues = (
        Issue.objects.select_related("client", "paralegal", "lawyer")
        .prefetch_related("issuenote_set")
        .filter(is_open=True)
        .exclude(paralegal__isnull=True)
        .annotate(next_review=Max("issuenote__event"))
        .order_by("next_review")
    )
    return _annotate_with_checks(issues)


def _annotate_issue_review_color(issues):
    # Annotate issues with days from now
    now = timezone.now()
    for issue in issues:
        if not issue.next_review:
            issue.color = ""
            continue

        days = (issue.next_review - now).days
        if days >= 7:
            issue.color = ""
        elif days >= 3:
            issue.color = "green"
        elif days >= 2:
            issue.color = "yellow"
        elif days >= 0:
            issue.color = "orange"
        else:
            issue.color = "red"


@checks_route
@coordinator_or_better_required
@require_http_methods(["GET"])
def case_checks_view(request):
    """Page where coordinators can see new cases which are missing manual checks"""
    issues = (
        Issue.objects.select_related("client", "paralegal")
        .prefetch_related("issuenote_set")
        .filter(is_open=True)
        .exclude(paralegal__isnull=True)
        .annotate(next_review=Max("issuenote__event"))
        .order_by("next_review")
    )
    issues = _annotate_with_checks(issues)
    alert_issues = [
        i
        for i in issues
        if i.stage != CaseStage.UNSTARTED
        and not (i.is_conflict_check and i.is_eligibility_check)
    ]
    context = {"alert_issues": alert_issues}
    return render(request, "case/case/checks_missing.html", context)


@inbox_route
@coordinator_or_better_required
@require_http_methods(["GET"])
def case_inbox_view(request):
    """Inbox page where coordinators can see new cases for them to assign"""
    is_unassigned = Q(paralegal__isnull=True)
    is_open = Q(is_open=True)
    is_inbox = is_unassigned & is_open
    issues = (
        Issue.objects.select_related("client", "paralegal")
        .filter(is_inbox)
        .order_by("created_at")
    )
    issues = _annotate_with_checks(issues)
    context = {"issues": issues}
    return render(request, "case/case/inbox.html", context)


def _annotate_with_checks(issue_qs):
    is_conflict_check = Q(note_type=NoteType.CONFLICT_CHECK_FAILURE) | Q(
        note_type=NoteType.CONFLICT_CHECK_SUCCESS
    )
    conflict_check_subquery = IssueNote.objects.filter(is_conflict_check).filter(
        issue=OuterRef("pk")
    )
    is_eligibility_check = Q(note_type=NoteType.ELIGIBILITY_CHECK_FAILURE) | Q(
        note_type=NoteType.ELIGIBILITY_CHECK_SUCCESS
    )
    eligibility_check_subquery = IssueNote.objects.filter(is_eligibility_check).filter(
        issue=OuterRef("pk")
    )
    return issue_qs.annotate(
        is_conflict_check=Exists(conflict_check_subquery)
    ).annotate(is_eligibility_check=Exists(eligibility_check_subquery))
