import logging

from django.db.models import Count, Max, Q
from django.views.decorators.http import require_http_methods
from django.http import Http404
from django.shortcuts import render
from django.utils import timezone

from django.contrib.auth.models import Group


from accounts.models import User, CaseGroups


from accounts.models import User
from case.forms import (
    DynamicTableForm,
    UserDetailsDynamicForm,
)
from case.views.auth import coordinator_or_better_required, admin_or_better_required
from case.utils.router import Router
from microsoft.service import get_user_permissions
from microsoft.tasks import refresh_ms_permissions

router = Router("user")
router.create_route("perms-resync").pk("pk").path("perms").path("resync")
router.create_route("perms-promote").pk("pk").path("perms").path("promote")
router.create_route("perms-demote").pk("pk").path("perms").path("demote")
router.create_route("perms").pk("pk").path("perms")
router.create_route("detail").pk("pk").slug("form_slug", optional=True)

ACCOUNT_DETAILS_FORMS = {
    "details": UserDetailsDynamicForm,
}


@router.use_route("detail")
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


@router.use_route("perms")
@coordinator_or_better_required
@require_http_methods(["GET", "POST"])
def account_detail_permissions_view(request, pk):
    try:
        user = User.objects.prefetch_related("groups").get(pk=pk)
    except User.DoesNotExist:
        raise Http404()

    fifteen_minutes_ago = timezone.now() - timezone.timedelta(minutes=15)
    is_ms_account_set_up = user.ms_account_created_at and (
        user.ms_account_created_at < fifteen_minutes_ago
    )
    perms = None
    try:
        perms = get_user_permissions(user)
    except Exception:
        logging.exception("Failed to load user account permissions from Microsoft")

    context = {
        "user": user,
        "is_ms_account_set_up": is_ms_account_set_up,
        "is_perms_load_success": bool(perms),
        "is_paralegal": user.groups.filter(name=CaseGroups.PARALEGAL).exists(),
        "is_coordinator": user.groups.filter(name=CaseGroups.COORDINATOR).exists(),
        "is_admin": user.is_superuser
        or user.groups.filter(name=CaseGroups.ADMIN).exists(),
    }
    if perms:
        context["has_coordinator_perms"] = perms["has_coordinator_perms"]
        context["paralegal_perm_issues"] = perms["paralegal_perm_issues"]
        context["paralegal_perm_missing_issues"] = perms[
            "paralegal_perm_missing_issues"
        ]
    return render(request, "case/accounts/_detail_perms.html", context)


@router.use_route("perms-resync")
@coordinator_or_better_required
@require_http_methods(["POST"])
def account_detail_perms_resync_view(request, pk):
    try:
        user = User.objects.prefetch_related("groups").get(pk=pk)
    except User.DoesNotExist:
        raise Http404()

    refresh_ms_permissions(user)
    return account_detail_permissions_view(request, pk)


@router.use_route("perms-promote")
@admin_or_better_required
@require_http_methods(["POST"])
def account_detail_perms_promote_view(request, pk):
    try:
        user = User.objects.prefetch_related("groups").get(pk=pk)
    except User.DoesNotExist:
        raise Http404()

    is_paralegal = user.groups.filter(name=CaseGroups.PARALEGAL).exists()
    if is_paralegal:
        group = Group.objects.get(name=CaseGroups.COORDINATOR)
        user.groups.add(group)
    else:
        group = Group.objects.get(name=CaseGroups.PARALEGAL)
        user.groups.add(group)
        refresh_ms_permissions(user)

    return account_detail_permissions_view(request, pk)


@router.use_route("perms-demote")
@admin_or_better_required
@require_http_methods(["POST"])
def account_detail_perms_demote_view(request, pk):
    try:
        user = User.objects.prefetch_related("groups").get(pk=pk)
    except User.DoesNotExist:
        raise Http404()

    is_paralegal = user.groups.filter(name=CaseGroups.PARALEGAL).exists()
    is_coordinator = user.groups.filter(name=CaseGroups.COORDINATOR).exists()
    group_name = None
    if is_coordinator:
        group_name = CaseGroups.COORDINATOR
    elif is_paralegal:
        group_name = CaseGroups.PARALEGAL

    if group_name:
        group = Group.objects.get(name=group_name)
        user.groups.remove(group)

    return account_detail_permissions_view(request, pk)
