from django.http import Http404
from rest_framework.decorators import api_view
from rest_framework.exceptions import PermissionDenied
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import UpdateModelMixin, RetrieveModelMixin

from case.utils.react import render_react_page
from case.serializers import TenancySerializer
from core.models import Tenancy
from .auth import paralegal_or_better_required, CoordinatorOrBetterCanWritePermission


@api_view(["GET"])
@paralegal_or_better_required
def tenancy_detail_page_view(request, pk):
    try:
        tenancy = Tenancy.objects.get(pk=pk)
    except Tenancy.DoesNotExist:
        raise Http404()

    has_object_permission = tenancy.check_permission(request.user)
    if not (has_object_permission or request.user.is_coordinator_or_better):
        raise PermissionDenied()

    context = {"tenancy": TenancySerializer(instance=tenancy).data}
    return render_react_page(request, "Tenancy", "tenancy-detail", context)


class TenancyApiViewset(GenericViewSet, RetrieveModelMixin, UpdateModelMixin):
    queryset = Tenancy.objects.all()
    serializer_class = TenancySerializer
    permission_classes = [CoordinatorOrBetterCanWritePermission]
