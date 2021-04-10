from urllib.parse import urlencode

from django.db.models import Max, Count, Q
from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView as BaseLoginView
from django.shortcuts import redirect, render
from django.core.paginator import Paginator
from django.http import Http404
from django.contrib import messages

from core.models import Issue
from .forms import IssueProgressForm, IssueSearchForm

PARALEGAL_CAPACITY = 4.0


def robots_view(request):
    """robots.txt for web crawlers"""
    return render(request, "case/robots.txt", content_type="text/plain")


def root_view(request):
    return redirect("case-list")


# FIXME: Permissions
@login_required
def paralegal_detail_view(request, pk):
    try:
        paralegal = (
            User.objects.filter(issue__isnull=False)
            .prefetch_related("issue_set")
            .distinct()
            .annotate(
                latest_issue_created_at=Max("issue__created_at"),
                total_cases=Count("issue"),
                open_cases=Count("issue", Q(issue__is_open=True)),
                open_repairs=Count(
                    "issue", Q(issue__is_open=True, issue__topic="REPAIRS")
                ),
                open_rent_reduction=Count(
                    "issue", Q(issue__is_open=True, issue__topic="RENT_REDUCTION")
                ),
                open_eviction=Count(
                    "issue", Q(issue__is_open=True, issue__topic="EVICTION")
                ),
            )
            .get(pk=pk)
        )
    except User.DoesNotExist:
        raise Http404()

    context = {
        "paralegal": paralegal,
    }
    return render(request, "case/paralegal_detail.html", context)


# FIXME: Permissions
@login_required
def paralegal_list_view(request):
    paralegals = (
        User.objects.filter(issue__isnull=False)
        .prefetch_related("issue_set")
        .distinct()
        .annotate(
            latest_issue_created_at=Max("issue__created_at"),
            total_cases=Count("issue"),
            open_cases=Count("issue", Q(issue__is_open=True)),
            open_repairs=Count("issue", Q(issue__is_open=True, issue__topic="REPAIRS")),
            open_rent_reduction=Count(
                "issue", Q(issue__is_open=True, issue__topic="RENT_REDUCTION")
            ),
            open_eviction=Count(
                "issue", Q(issue__is_open=True, issue__topic="EVICTION")
            ),
        )
        .order_by("-latest_issue_created_at")
    )
    for p in paralegals:
        p.capacity = 100 * p.open_cases / PARALEGAL_CAPACITY

    context = {
        "paralegals": paralegals,
    }
    return render(request, "case/paralegal_list.html", context)


# FIXME: Permissions
@login_required
def case_list_view(request):
    form = IssueSearchForm(request.GET)
    issue_qs = Issue.objects.select_related("client", "paralegal")
    issues = form.search(issue_qs).order_by("-created_at").all()
    page, next_qs, prev_qs = _get_page(request, issues, per_page=14)
    context = {
        "issue_page": page,
        "form": form,
        "next_qs": next_qs,
        "prev_qs": prev_qs,
    }
    return render(request, "case/case_list.html", context)


# FIXME: Permissions
@login_required
def case_detail_view(request, pk):
    context = _get_case_detail_context(request, pk)
    return render(request, "case/case_detail.html", context)


# FIXME: Permissions
@login_required
def case_detail_progress_view(request, pk):
    context = _get_case_detail_context(request, pk)
    # FIXME: Permissions
    if request.method == "POST":
        form = IssueProgressForm(request.POST, instance=context["issue"])
        if form.is_valid():
            form.save()
            messages.success(request, "Update successful")
    else:
        form = IssueProgressForm(instance=context["issue"])

    context = {**context, "form": form}
    return render(request, "case/case_detail_progress.html", context)


def _get_case_detail_context(request, pk):
    try:
        issue = Issue.objects.select_related("client").get(pk=pk)
    except Issue.DoesNotExist:
        raise Http404()

    # FIXME: Assume only only tenancy but that's not how the models work.
    tenancy = issue.client.tenancy_set.first()

    if issue.actionstep_id:
        actionstep_url = _get_actionstep_url(issue.actionstep_id)
    else:
        actionstep_url = None

    return {
        "issue": issue,
        "tenancy": tenancy,
        "actionstep_url": actionstep_url,
    }


def _get_page(request, items, per_page):
    page_number = request.GET.get("page", 1) or 1
    paginator = Paginator(items, per_page=per_page)
    page = paginator.get_page(page_number)
    next_page_num = page.next_page_number() if page.has_next() else paginator.num_pages
    prev_page_num = page.previous_page_number() if page.has_previous() else 1
    get_query = {k: v for k, v in request.GET.items()}
    next_qs = "?" + urlencode({**get_query, "page": next_page_num})
    prev_qs = "?" + urlencode({**get_query, "page": prev_page_num})
    return page, next_qs, prev_qs


class LoginView(BaseLoginView):
    template_name = "case/login.html"
    redirect_authenticated_user = True


login_view = LoginView.as_view()


def logout_view(request):
    logout(request)
    return redirect(settings.LOGIN_URL)


def _get_actionstep_url(actionstep_id):
    return f"https://ap-southeast-2.actionstep.com/mym/asfw/workflow/action/overview/action_id/{actionstep_id}"
