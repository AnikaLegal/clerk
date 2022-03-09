from django.db.models import Count, Max, Q
from django.shortcuts import render

from accounts.models import User
from .auth import coordinator_or_better_required
from case.utils.router import Router

PARALEGAL_CAPACITY = 4.0


router = Router("paralegal")
router.create_route("list")


@router.use_route("list")
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
            open_bonds=Count("issue", Q(issue__is_open=True, issue__topic="BONDS")),
            open_eviction=Count(
                "issue", Q(issue__is_open=True, issue__topic="EVICTION")
            ),
        )
        .order_by("-latest_issue_created_at")
    )
    for p in paralegals:
        p.capacity = 100 * p.open_cases / p.case_capacity

    context = {
        "paralegals": paralegals,
    }
    return render(request, "case/paralegal_list.html", context)
