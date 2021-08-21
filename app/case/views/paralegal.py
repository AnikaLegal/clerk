from django.db.models import Count, Max, Q
from django.http import Http404
from django.shortcuts import render

from accounts.models import User
from case.forms import UserDetailsDynamicForm, DynamicTableForm

from .auth import coordinator_or_better_required

PARALEGAL_CAPACITY = 4.0

PARALEGAL_DETAILS_FORMS = {
    "form": UserDetailsDynamicForm,
}


@coordinator_or_better_required
def paralegal_detail_view(request, pk, form_slug: str = ""):
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

    forms = DynamicTableForm.build_forms(
        request, form_slug, paralegal, PARALEGAL_DETAILS_FORMS
    )
    context = {"paralegal": paralegal, "forms": forms}
    form_resp = DynamicTableForm.get_response(request, form_slug, forms, context)
    if form_resp:
        return form_resp
    else:
        return render(request, "case/paralegal_detail.html", context)


@coordinator_or_better_required
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
