from caller.models import Call
from core.models.issue import CaseTopic
from django.db.models import QuerySet
from rest_framework.decorators import api_view
from rest_framework.mixins import ListModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet
from webhooks.models import WebflowContact

from case.serializers.enquiry import (
    CallSearchSerializer,
    CallSerializer,
    ContactSearchSerializer,
    ContactSerializer,
)
from case.utils import ClerkPaginator, render_react_page
from case.views.auth import (
    CoordinatorOrBetterPermission,
    coordinator_or_better_required,
)


@api_view(["GET"])
@coordinator_or_better_required
def enquiry_list_page_view(request):
    # All topics, not just active ones: older calls can have retired topics.
    context = {
        "topic_options": [
            {"value": value, "label": label} for value, label in CaseTopic.CHOICES
        ],
    }
    return render_react_page(request, "Enquiries", "enquiry-list", context)


class EnquiryPaginator(ClerkPaginator):
    page_size = 20


class EnquiryApiViewset(GenericViewSet, ListModelMixin, UpdateModelMixin):
    """
    Lists people who contacted us outside the intake form, and lets staff
    record their follow-up.
    """

    pagination_class = EnquiryPaginator
    permission_classes = [CoordinatorOrBetterPermission]
    # PATCH only: a PUT would need every field, and only three can change.
    http_method_names = ["get", "patch", "head", "options"]
    search_serializer_class: type

    def get_queryset(self) -> QuerySet:
        queryset = self.queryset.order_by("-created_at")
        if self.action == "list":
            serializer = self.search_serializer_class(
                data=self.request.query_params, partial=True
            )
            serializer.is_valid(raise_exception=True)
            queryset = queryset.filter(**serializer.validated_data)
        return queryset


class CallApiViewset(EnquiryApiViewset):
    queryset = Call.objects.all()
    serializer_class = CallSerializer
    search_serializer_class = CallSearchSerializer


class ContactApiViewset(EnquiryApiViewset):
    queryset = WebflowContact.objects.all()
    serializer_class = ContactSerializer
    search_serializer_class = ContactSearchSerializer
