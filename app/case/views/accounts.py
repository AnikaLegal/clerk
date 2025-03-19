import logging
from typing import Optional

from accounts.models import CaseGroups, User
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.db.models import Q, QuerySet
from django.http import Http404
from django.urls import reverse
from django_q.tasks import async_task
from microsoft.service import get_user_permissions
from microsoft.tasks import refresh_ms_permissions, set_up_new_user_task
from rest_framework.decorators import action, api_view
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from case.serializers import (
    AccountSearchSerializer,
    AccountSortSerializer,
    IssueSerializer,
    UserCreateSerializer,
    UserSerializer,
)
from case.utils.react import render_react_page
from case.views.auth import (
    CoordinatorOrBetterPermission,
    ParalegalOrBetterObjectPermission,
    coordinator_or_better_required,
    paralegal_or_better_required,
)

logger = logging.getLogger(__name__)


@api_view(["GET"])
@paralegal_or_better_required
def account_list_page_view(request):
    context = {
        "create_url": reverse("account-create"),
        "groups": list(Group.objects.values_list("name", flat=True)),
    }
    return render_react_page(request, "Accounts", "accounts-list", context)


@api_view(["GET"])
@paralegal_or_better_required
def account_detail_page_view(request, pk):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        raise Http404()

    name = user.get_full_name()
    context = {
        "account_id": user.id,
        "current_user_id": request.user.id,
    }
    return render_react_page(request, f"User {name}", "account-detail", context)


@api_view(["GET"])
@coordinator_or_better_required
def account_create_page_view(request):
    return render_react_page(request, "Invite paralegal", "account-create", {})


class AccountApiViewset(
    GenericViewSet, UpdateModelMixin, ListModelMixin, RetrieveModelMixin
):
    serializer_class = UserSerializer

    def get_permissions(self):
        if (
            self.action == "list"
            or self.action == "retrieve"
            or self.action == "get_account_detail_permissions"
        ):
            permission_classes = [
                CoordinatorOrBetterPermission | ParalegalOrBetterObjectPermission
            ]
        else:
            permission_classes = [CoordinatorOrBetterPermission]

        return [p() for p in permission_classes]

    def get_queryset(self):
        user = self.request.user

        queryset = User.objects.all()
        queryset = queryset.prefetch_related("groups")

        if self.action == "list":
            queryset = self.sort_queryset(queryset)
            queryset = self.search_queryset(queryset)

            if user.is_paralegal or user.is_lawyer:
                # Paralegals & lawyers can only view their own & so-called
                # system accounts.
                query = Q(id=user.id)
                query |= Q(is_system_account=True)
                queryset = queryset.filter(query)

        return queryset

    def sort_queryset(self, queryset: QuerySet[User]) -> QuerySet[User]:
        serializer = AccountSortSerializer(data=self.request.query_params, partial=True)
        serializer.is_valid(raise_exception=True)
        sort = serializer.validated_data.get("sort", ["-date_joined"])
        return queryset.order_by(*sort)

    def search_queryset(self, queryset: QuerySet[User]) -> QuerySet[User]:
        """
        Filter queryset by search terms in query params
        """
        search_query_serializer = AccountSearchSerializer(
            data=self.request.query_params, partial=True
        )
        search_query_serializer.is_valid(raise_exception=True)
        search_query = search_query_serializer.validated_data

        for key, value in search_query.items():
            if value is not None:
                if key == "name":
                    queryset = queryset.filter(
                        Q(first_name__icontains=value) | Q(last_name__icontains=value)
                    )
                elif key == "group":
                    queryset = queryset.filter(groups__name=value)
                else:
                    # Apply basic field filtering
                    queryset = queryset.filter(**{key: value})

        return queryset

    def create(self, request, *args, **kwargs):
        """Invite a paralegal to join the platform"""
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        user = User.objects.filter(email=email).last()
        if not user:
            user = serializer.save()

        async_task(set_up_new_user_task, user.pk)
        return Response(serializer.data, status=201)

    @action(
        detail=True,
        methods=["GET"],
        url_path="perms",
        url_name="perms",
    )
    def get_account_detail_permissions(self, request, pk):
        user = self.get_object()
        #
        if not request.user.is_coordinator_or_better and user != request.user:
            raise PermissionDenied
        perms_data = _load_ms_permissions(user)
        return Response(perms_data)

    @action(
        detail=True,
        methods=["POST"],
        url_path="perms-resync",
        url_name="perms-resync",
    )
    def account_detail_perms_resync_view(self, request, pk):
        try:
            user = User.objects.prefetch_related("groups").get(pk=pk)
        except User.DoesNotExist:
            raise Http404()

        refresh_ms_permissions(user)
        perms_data = _load_ms_permissions(user)
        return Response(
            {"account": UserSerializer(user).data, "permissions": perms_data}
        )

    @action(
        detail=True,
        methods=["POST"],
        url_path="perms-promote",
        url_name="perms-promote",
    )
    def account_detail_perms_promote_view(self, request, pk):
        if not request.user.is_admin_or_better:
            raise PermissionDenied

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

        perms_data = _load_ms_permissions(user)
        return Response(
            {"account": UserSerializer(user).data, "permissions": perms_data}
        )

    @action(
        detail=True,
        methods=["POST"],
        url_path="perms-demote",
        url_name="perms-demote",
    )
    def account_detail_perms_demote_view(self, request, pk):
        if not request.user.is_admin_or_better:
            raise PermissionDenied

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

        perms_data = _load_ms_permissions(user)
        return Response(
            {"account": UserSerializer(user).data, "permissions": perms_data}
        )


def _load_ms_permissions(user) -> Optional[dict]:
    try:
        perms = get_user_permissions(user)
    except Exception:
        logger.exception("Failed to load user account permissions from Microsoft")
        return

    return {
        "has_coordinator_perms": perms.has_coordinator_perms,
        "paralegal_perm_issues": IssueSerializer(
            perms.paralegal_perm_issues, many=True
        ).data,
        "paralegal_perm_missing_issues": IssueSerializer(
            perms.paralegal_perm_missing_issues, many=True
        ).data,
    }
