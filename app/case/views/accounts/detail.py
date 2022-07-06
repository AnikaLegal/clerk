import logging

from django.views.decorators.http import require_http_methods
from django.http import Http404
from django.shortcuts import render
from django.utils import timezone
from django.contrib.auth.models import Group
from rest_framework.decorators import api_view
from rest_framework.response import Response

from accounts.models import User, CaseGroups
from case.utils.react import render_react_page
from accounts.models import User
from case.views.auth import coordinator_or_better_required, admin_or_better_required
from case.utils.router import Router
from case.serializers import UserDetailSerializer, IssueListSerializer
from microsoft.service import get_user_permissions
from microsoft.tasks import refresh_ms_permissions

router = Router("user")
router.create_route("perms-resync").pk("pk").path("perms").path("resync")
router.create_route("perms-promote").pk("pk").path("perms").path("promote")
router.create_route("perms-demote").pk("pk").path("perms").path("demote")
router.create_route("perms").pk("pk").path("perms")
router.create_route("detail").pk("pk")

logger = logging.getLogger(__name__)


@router.use_route("detail")
@api_view(["GET", "PATCH"])
@coordinator_or_better_required
def account_detail_view(request, pk, form_slug: str = ""):
    try:
        user = (
            User.objects.prefetch_related(
                "groups",
                "issue_notes",
                "issue_set__paralegal__groups",
                "issue_set__lawyer__groups",
                "issue_set__client",
                "lawyer_issues__paralegal__groups",
                "lawyer_issues__lawyer__groups",
                "lawyer_issues__client",
            )
            .distinct()
            .get(pk=pk)
        )
    except User.DoesNotExist:
        raise Http404()

    if request.method == "GET":
        name = user.get_full_name()
        context = {"account": UserDetailSerializer(user).data}
        return render_react_page(request, f"Client {name}", "account-detail", context)
    elif request.method == "PATCH":
        serializer = UserDetailSerializer(
            instance=user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"account": serializer.data})


@router.use_route("perms")
@coordinator_or_better_required
@api_view(["GET"])
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
        logger.exception("Failed to load user account permissions from Microsoft")

    data = {
        "is_ms_account_set_up": is_ms_account_set_up,
        "is_perms_load_success": bool(perms),
    }
    if perms:
        data["has_coordinator_perms"] = perms["has_coordinator_perms"]
        data["paralegal_perm_issues"] = perms["paralegal_perm_issues"]
        data["paralegal_perm_missing_issues"] = IssueListSerializer(
            perms["paralegal_perm_missing_issues"], many=True
        ).data
    else:
        data["has_coordinator_perms"] = False
        data["paralegal_perm_issues"] = []
        data["paralegal_perm_missing_issues"] = []

    return Response(data)


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
