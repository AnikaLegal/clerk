from django.db.models import Count, Max, Q, F, Case, When

from accounts.models import User
from .auth import coordinator_or_better_required
from case.utils.router import Router
from case.utils.react import render_react_page
from case.serializers import ParalegalSerializer
from accounts.models import CaseGroups

router = Router("paralegal")
router.create_route("list")


@router.use_route("list")
@coordinator_or_better_required
def paralegal_list_view(request):
    paralegals = User.objects.filter(
        groups__name__in=[CaseGroups.PARALEGAL, CaseGroups.COORDINATOR]
    ).prefetch_related("issue_set", "groups")
    lawyers = User.objects.filter(groups__name=CaseGroups.LAWYER).prefetch_related(
        "issue_set", "groups"
    )
    paralegals = _calculate_user_capacity(paralegals, "issue")
    lawyers = _calculate_user_capacity(lawyers, "lawyer_issue")
    context = {
        "paralegals": ParalegalSerializer(paralegals, many=True).data,
        "lawyers": ParalegalSerializer(lawyers, many=True).data,
    }
    return render_react_page(request, f"Paralegals", "paralegal-list", context)


def _calculate_user_capacity(user_qs, issue_rel):
    user_qs = (
        user_qs.annotate(
            latest_issue_created_at=Max(f"{issue_rel}__created_at"),
            total_cases=Count(issue_rel, distinct=True),
            open_cases=Count(
                issue_rel, Q(**{f"{issue_rel}__is_open": True}), distinct=True
            ),
            open_repairs=Count(
                issue_rel,
                Q(**{f"{issue_rel}__is_open": True, f"{issue_rel}__topic": "REPAIRS"}),
                distinct=True,
            ),
            open_bonds=Count(
                issue_rel,
                Q(**{f"{issue_rel}__is_open": True, f"{issue_rel}__topic": "BONDS"}),
                distinct=True,
            ),
            open_eviction=Count(
                issue_rel,
                Q(**{f"{issue_rel}__is_open": True, f"{issue_rel}__topic": "EVICTION"}),
                distinct=True,
            ),
        )
        .annotate(
            capacity=Case(
                When(case_capacity=0, then=-1),
                default=100 * F("open_cases") / F("case_capacity"),
            )
        )
        .order_by("-capacity")
    )
    return user_qs