from django.db.models import Count, Max, Q
from django.views.decorators.http import require_http_methods
from django.http import Http404
from django.shortcuts import render

from accounts.models import User
from case.forms import (
    DynamicTableForm,
    UserDetailsDynamicForm,
    UserPermissionsDynamicForm,
)
from case.views.auth import coordinator_or_better_required
from case.utils.router import Route

detail_route = Route("detail").pk("pk").slug("form_slug", optional=True)

ACCOUNT_DETAILS_FORMS = {
    "details": UserDetailsDynamicForm,
    "permissions": UserPermissionsDynamicForm,
}


@detail_route
@require_http_methods(["GET", "POST"])
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
        request, form_slug, user, ACCOUNT_DETAILS_FORMS, extra_kwargs
    )
    context = {"user": user, "forms": forms}
    form_resp = DynamicTableForm.get_response(request, form_slug, forms, context)
    if form_resp:
        return form_resp
    else:
        return render(request, "case/accounts/detail.html", context)
