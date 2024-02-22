from django.http import Http404
from rest_framework.decorators import api_view
from rest_framework.exceptions import PermissionDenied
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import UpdateModelMixin

from case.serializers import ClientSerializer, IssueSerializer
from core.models import Client
from case.utils.react import render_react_page
from .auth import (
    paralegal_or_better_required,
    CoordinatorOrBetterCanWritePermission,
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


class ClientApiViewset(GenericViewSet, UpdateModelMixin):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [
        CoordinatorOrBetterCanWritePermission | ParalegalOrBetterObjectPermission
    ]
