from django.db.models import Count, Max, Q, F, Case, When
from django.shortcuts import render

from accounts.models import User
from .auth import coordinator_or_better_required
from case.utils.router import Router
from case.forms import ParalegalSearchForm

router = Router("paralegal")
router.create_route("list")
router.create_route("search").path("search")


@router.use_route("list")
@coordinator_or_better_required
def paralegal_list_view(request):
    paralegals = (
        User.objects.filter(Q(groups__name="Paralegal") | Q(groups__name="Coordinator"))
        .prefetch_related("issue_set")
        .distinct()
    )
    paralegals = _calculate_user_capacity(paralegals, "issue")

    lawyers = (
        User.objects.filter(groups__name="Lawyer")
        .prefetch_related("issue_set")
        .distinct()
    )
    lawyers = _calculate_user_capacity(lawyers, "lawyer_issue")
    form = ParalegalSearchForm()
    context = {"paralegals": paralegals, "lawyers": lawyers, "form": form}
    return render(request, "case/paralegals/paralegal_list.html", context)


@router.use_route("search")
@coordinator_or_better_required
def paralegal_search_view(request):
    form = ParalegalSearchForm(request.GET)
    paralegals = (
        User.objects.filter(groups__name="Paralegal")
        .prefetch_related("issue_set")
        .distinct()
    )
    paralegals = _calculate_user_capacity(paralegals, "issue")
    paralegals = form.search_queryset(paralegals)
    context = {"users": paralegals, "table_id": "paralegal-table"}
    return render(request, "case/paralegals/_list_results.html", context)


def _calculate_user_capacity(user_qs, issue_rel):
    user_qs = (
        user_qs.annotate(
            latest_issue_created_at=Max(f"{issue_rel}__created_at"),
            total_cases=Count(issue_rel),
            open_cases=Count(issue_rel, Q(**{f"{issue_rel}__is_open": True})),
            open_repairs=Count(
                issue_rel,
                Q(**{f"{issue_rel}__is_open": True, f"{issue_rel}__topic": "REPAIRS"}),
            ),
            open_bonds=Count(
                issue_rel,
                Q(**{f"{issue_rel}__is_open": True, f"{issue_rel}__topic": "BONDS"}),
            ),
            open_eviction=Count(
                issue_rel,
                Q(**{f"{issue_rel}__is_open": True, f"{issue_rel}__topic": "EVICTION"}),
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