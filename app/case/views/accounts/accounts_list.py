from typing import List
from django.db.models import Q
from django.views.decorators.http import require_http_methods
from django.shortcuts import render

from accounts.models import User
from case.views.auth import coordinator_or_better_required


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
