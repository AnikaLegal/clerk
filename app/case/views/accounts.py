import logging
from typing import Optional

from accounts.models import CaseGroups, User
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.db.models import Q, QuerySet
from django.http import Http404
from django.urls import reverse
from django_q.tasks import async_task
from google.service import list_directory_users
from microsoft.service import get_user_permissions
from microsoft.tasks import (
    reset_ms_access,
    set_up_new_user_task,
)
from rest_framework.decorators import action, api_view
from rest_framework.mixins import ListModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from case.serializers import (
    AccountSearchSerializer,
    AccountSortSerializer,
    IssueNoteSerializer,
    IssueSerializer,
    PotentialUserSerializer,
    UserCreateSerializer,
    UserSerializer,
)
from case.utils.react import render_react_page
from case.views.auth import (
    AdminOrBetterPermission,
    CoordinatorOrBetterPermission,
    coordinator_or_better_required,
    paralegal_or_better_required,
)

logger = logging.getLogger(__name__)


@api_view(["GET"])
@paralegal_or_better_required
def account_list_page_view(request):
    users = User.objects.prefetch_related("groups").order_by("-date_joined").all()
    context = {
        "users": UserSerializer(users, many=True).data,
        "create_url": reverse("account-create"),
    }
    return render_react_page(request, "Accounts", "accounts-list", context)


@api_view(["GET"])
@coordinator_or_better_required
def account_detail_page_view(request, pk):
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

    name = user.get_full_name()
    context = {
        "account": UserSerializer(user).data,
        "issue_set": IssueSerializer(user.issue_set.all(), many=True).data,
        "lawyer_issues": IssueSerializer(user.lawyer_issues.all(), many=True).data,
        "performance_notes": IssueNoteSerializer(
            user.issue_notes.all(), many=True
        ).data,
    }
    return render_react_page(request, f"User {name}", "account-detail", context)


@api_view(["GET"])
@coordinator_or_better_required
def account_create_page_view(request):
    return render_react_page(request, "Invite paralegal", "account-create", {})


class AccountApiViewset(GenericViewSet, UpdateModelMixin, ListModelMixin):
    serializer_class = UserSerializer
    permission_classes = [CoordinatorOrBetterPermission]

    def get_queryset(self):
        queryset = User.objects.prefetch_related("groups").all()

        if self.action == "list":
            queryset = self.sort_queryset(queryset)
            queryset = self.search_queryset(queryset)

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
        try:
            user = User.objects.prefetch_related("groups").get(pk=pk)
        except User.DoesNotExist:
            raise Http404()

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

        reset_ms_access(user)
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
            reset_ms_access(user)

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

    @action(
        detail=False,
        methods=["GET"],
        url_path="potential",
        url_name="potential",
        permission_classes=[AdminOrBetterPermission],
    )
    def account_list_potential_users(self, request):
        # Fetch active users from Google Directory.
        active_users = [
            user
            for user in list_directory_users(
                subject_email=request.user.email,
            )
            if user.get("suspended") is False
        ]

        # Exclude users that are already in the system.
        existing_emails = set(self.get_queryset().values_list("email", flat=True))
        potential_users = [
            user for user in active_users if user["primaryEmail"] not in existing_emails
        ]
        potential_users.sort(key=lambda u: u["primaryEmail"])

        serializer = PotentialUserSerializer(potential_users, many=True)
        return Response(serializer.data)


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
