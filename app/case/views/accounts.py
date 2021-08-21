from typing import List
from django.db.models import Count, Max, Q
from django.views.decorators.http import require_http_methods
from django.http import Http404
from django.shortcuts import render

from accounts.models import User, CaseGroups
from case.forms import (
    UserDetailsDynamicForm,
    DynamicTableForm,
    UserPermissionsDynamicForm,
)
from .auth import coordinator_or_better_required

PARALEGAL_CAPACITY = 4.0
PARALEGAL_DETAILS_FORMS = {
    "details": UserDetailsDynamicForm,
    "permissions": UserPermissionsDynamicForm,
}
ADMIN_GROUPS = [CaseGroups.PARALEGAL, CaseGroups.COORDINATOR]
COORDINATOR_GROUPS = [CaseGroups.PARALEGAL]


@require_http_methods(["GET"])
@coordinator_or_better_required
def account_list_view(request):
    users = (
        User.objects.prefetch_related("groups")
        .order_by("-date_joined")
        .filter(is_active=True)
        .all()
    )
    context = {}
    if "name" in request.GET or "groups" in request.GET:
        name, groups = request.GET.get("name"), request.GET.get("groups")
        queries = []
        if name:
            queries.append(Q(first_name__icontains=name))
            queries.append(Q(last_name__icontains=name))
        if groups:
            for group in groups.split(","):
                queries.append(Q(groups__name=group))

        if queries:
            users = users.filter(combine_q_with_or(queries))

        context["users"] = users
        return render(request, "case/snippets/_account_list_table.html", context)
    else:
        context["users"] = users
        return render(request, "case/account_list.html", context)


def combine_q_with_or(queries: List[Q]) -> Q:
    assert queries, "List of Q expressions cannot be empty"
    query = None
    for q in queries:
        if query:
            query |= q
        else:
            query = q

    return query


@coordinator_or_better_required
def account_detail_view(request, pk, form_slug: str = ""):
    try:
        user = (
            User.objects.prefetch_related("issue_set")
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

    extra_kwargs = {"permissions": {"requesting_user": request.user}}
    forms = DynamicTableForm.build_forms(
        request, form_slug, user, PARALEGAL_DETAILS_FORMS, extra_kwargs
    )
    context = {"user": user, "forms": forms}
    form_resp = DynamicTableForm.get_response(request, form_slug, forms, context)
    if form_resp:
        return form_resp
    else:
        return render(request, "case/account_detail.html", context)
