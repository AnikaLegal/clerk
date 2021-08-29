from django.db.models import Count, Max, Q
from django.shortcuts import render

from accounts.models import User
from .auth import coordinator_or_better_required

PARALEGAL_CAPACITY = 4.0


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
