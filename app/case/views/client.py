from django.http import Http404
from django.db.models import Q, QuerySet, Value
from django.db.models.functions import Concat, Trim
from rest_framework.decorators import api_view
from rest_framework.exceptions import PermissionDenied
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (
    UpdateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
)


from case.serializers import (
    ClientSerializer,
    IssueSerializer,
    ClientSearchSerializer,
)
from core.models import Client
from case.utils import render_react_page, ClerkPaginator
from .auth import (
    paralegal_or_better_required,
    CoordinatorOrBetterPermission,
    ParalegalOrBetterObjectPermission,
)


@api_view(["GET"])
@paralegal_or_better_required
def client_detail_page_view(request, pk):
    try:
        client = Client.objects.prefetch_related("issue_set").get(pk=pk)
    except Client.DoesNotExist:
        raise Http404()

    has_object_permission = client.check_permission(request.user)
    if not (has_object_permission or request.user.is_coordinator_or_better):
        raise PermissionDenied()

    name = client.get_full_name()
    context = {
        "client": ClientSerializer(client).data,
        "issues": IssueSerializer(
            client.issue_set.all(), read_only=True, many=True
        ).data,
    }
    return render_react_page(request, f"Client {name}", "client-detail", context)


class ClientPaginator(ClerkPaginator):
    page_size = 20


class ClientApiViewset(
    GenericViewSet,
    RetrieveModelMixin,
    ListModelMixin,
    UpdateModelMixin,
):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    pagination_class = ClientPaginator
    permission_classes = [
        CoordinatorOrBetterPermission | ParalegalOrBetterObjectPermission
    ]

    def get_queryset(self):
        queryset = self.queryset.order_by("-created_at")
        if self.action == "list":
            queryset = self.list_queryset(queryset)
        return queryset

    def list_queryset(self, queryset: QuerySet[Client]) -> QuerySet[Client]:
        """
        Restrict results & filter queryset by search terms in query params.
        """
        user = self.request.user

        if user.is_paralegal:
            # Paralegals can only see the clients from assigned cases
            queryset = queryset.filter(issue__paralegal=user)
        elif not user.is_coordinator_or_better:
            # If you're not a paralegal or coordinator+ you can't see nuthin.
            queryset = queryset.none()

        serializer = ClientSearchSerializer(
            data=self.request.query_params, partial=True
        )
        serializer.is_valid(raise_exception=True)
        search = serializer.validated_data.get("q", None)
        if search:
            q_filter = (
                Q(full_name__icontains=search)
                | Q(preferred_name__icontains=search)
                | Q(email__icontains=search)
                | Q(phone_number__icontains=search)
            )
            queryset = queryset.annotate(
                full_name=Concat(Trim("first_name"), Value(" "), Trim("last_name"))
            ).filter(q_filter)

        return queryset
