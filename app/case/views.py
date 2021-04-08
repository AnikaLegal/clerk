from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView as BaseLoginView
from django.shortcuts import redirect, render
from django.core.paginator import Paginator
from django.http import Http404

from core.models import Issue


def robots_view(request):
    """robots.txt for web crawlers"""
    return render(request, "case/robots.txt", content_type="text/plain")


def root_view(request):
    return redirect("case-list")


@login_required
def case_list_view(request):
    issues = Issue.objects.select_related("client").order_by("-created_at").all()
    page_size = 10
    page_number = request.GET.get("page", 1) or 1
    issue_paginator = Paginator(issues, page_size)
    issue_page = issue_paginator.get_page(page_number)
    context = {"issue_page": issue_page}
    return render(request, "case/case-list.html", context)


@login_required
def case_details_view(request, pk):
    try:
        issue = Issue.objects.select_related("client").get(pk=pk)
    except Issue.DoesNotExist:
        raise Http404()

    # FIXME: Assume only only tenancy but that's not how the models work.
    tenancy = issue.client.tenancy_set.first()

    # FIXME: hardcoded
    actionstep_url = _get_actionstep_url(719)

    context = {
        "issue": issue,
        "tenancy": tenancy,
        "actionstep_url": actionstep_url,
    }
    return render(request, "case/case-details.html", context)


class LoginView(BaseLoginView):
    template_name = "case/login.html"
    redirect_authenticated_user = True


login_view = LoginView.as_view()


def logout_view(request):
    logout(request)
    return redirect(settings.LOGIN_URL)


def _get_actionstep_url(actionstep_id):
    return f"https://ap-southeast-2.actionstep.com/mym/asfw/workflow/action/overview/action_id/{actionstep_id}"
