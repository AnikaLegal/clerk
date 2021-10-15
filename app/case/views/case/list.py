from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Max
from django.utils import timezone

from case.forms import IssueSearchForm
from case.utils import get_page
from core.models import Issue
from core.models.issue import CaseStage
from core.models.issue_note import NoteType

from case.views.auth import login_required, coordinator_or_better_required
from case.utils.router import Route

COORDINATORS_EMAIL = "coordinators@anikalegal.com"

list_route = Route("list")
search_route = Route("search").path("search")
inbox_route = Route("inbox").path("inbox")
review_route = Route("review").path("review")


@list_route
@login_required
@require_http_methods(["GET"])
def case_list_view(request):
    """
    List of all cases for paralegals and coordinators to view.
    """
    form = IssueSearchForm(request.GET)
    issue_qs = Issue.objects.select_related("client", "paralegal")

    if request.user.is_paralegal:
        # Paralegals can only see assigned cases
        issue_qs = issue_qs.filter(paralegal=request.user)
    elif not request.user.is_coordinator_or_better:
        issue_qs = issue_qs.none()

    issues = form.search(issue_qs).order_by("-created_at").all()
    page, next_qs, prev_qs = get_page(request, issues, per_page=28)
    context = {
        "issue_page": page,
        "form": form,
        "next_qs": next_qs,
        "prev_qs": prev_qs,
    }
    return render(request, "case/case/list.html", context)


@search_route
@login_required
@require_http_methods(["GET"])
def case_search_view(request):
    form = IssueSearchForm(request.GET)
    issue_qs = Issue.objects.select_related("client", "paralegal")
    if request.user.is_paralegal:
        # Paralegals can only see assigned cases
        issue_qs = issue_qs.filter(paralegal=request.user)
    elif not request.user.is_coordinator_or_better:
        issue_qs = issue_qs.none()

    issues = form.search(issue_qs).order_by("-created_at").all()
    page, next_qs, prev_qs = get_page(request, issues, per_page=28)
    context = {
        "issue_page": page,
        "form": form,
        "next_qs": next_qs,
        "prev_qs": prev_qs,
    }
    return render(request, "case/case/_list_results.html", context)


@review_route
@coordinator_or_better_required
@require_http_methods(["GET"])
def case_review_view(request):
    """Inbox page where coordinators can see new cases for them to review and assign"""
    is_open = Q(is_open=True)
    has_review = Q(issuenote__note_type=NoteType.REVIEW)
    is_review = is_open & has_review
    issues = (
        Issue.objects.select_related("client", "paralegal")
        .prefetch_related("issuenote_set")
        .filter(is_review)
        .annotate(next_review=Max("issuenote__event"))
        .order_by("next_review")
    )
    # Annotate issues with days from now
    now = timezone.now()
    for issue in issues:
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

    context = {"issues": issues}
    return render(request, "case/case/review.html", context)


@inbox_route
@coordinator_or_better_required
@require_http_methods(["GET"])
def case_inbox_view(request):
    """Inbox page where coordinators can see new cases for them to review and assign"""
    is_coordinators = Q(paralegal__email=COORDINATORS_EMAIL)
    is_open = Q(is_open=True)
    is_new_stage = Q(stage=CaseStage.UNSTARTED) | Q(stage__isnull=True)
    is_inbox = is_coordinators & is_open & is_new_stage
    issues = Issue.objects.select_related("client", "paralegal").filter(is_inbox)
    context = {"issues": issues}
    return render(request, "case/case/inbox.html", context)