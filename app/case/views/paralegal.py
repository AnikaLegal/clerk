from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Max, Q
from django.http import Http404
from django.shortcuts import render

from accounts.models import User
from case.forms import (
    ParalegalDetailsForm,
)

PARALEGAL_CAPACITY = 4.0


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

    # FIXME: Permissions
    if request.method == "POST":
        form = ParalegalDetailsForm(request.POST, instance=paralegal)
        if form.is_valid():
            form.save()
            messages.success(request, "Update successful")
    else:
        form = ParalegalDetailsForm(instance=paralegal)

    context = {"paralegal": paralegal, "form": form}
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
