import logging
from typing import Optional

from accounts.models import User, CaseGroups
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
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from case.serializers import (
    AccountSearchSerializer,
    AccountSortSerializer,
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
)

logger = logging.getLogger(__name__)


@api_view(["GET"])
@coordinator_or_better_required
def account_list_page_view(request):
    context = {
        "create_url": reverse("account-create"),
        "group_values": CaseGroups.values,
    }
    return render_react_page(request, "Accounts", "accounts-list", context)


@api_view(["GET"])
@coordinator_or_better_required
def account_detail_page_view(request, pk):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        raise Http404()

    name = user.get_full_name()
    context = {
        "account_id": pk,
    }
    return render_react_page(request, f"User {name}", "account-detail", context)


@api_view(["GET"])
@coordinator_or_better_required
def account_create_page_view(request):
    context = {
        "group_values": CaseGroups.values,
    }
    return render_react_page(request, "Invite paralegal", "account-create", context)


class AccountApiViewset(
    GenericViewSet, UpdateModelMixin, ListModelMixin, RetrieveModelMixin
):
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
        """Create a new user account and set up their Microsoft access asynchronously."""
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
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

        # TODO: remove user data from response.
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
            user for user in list_directory_users() if user.get("suspended") is False
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
