from django.db.models import Prefetch, QuerySet
from rest_framework.decorators import api_view
from rest_framework.mixins import CreateModelMixin, ListModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet

from caller.models import Call, Callback
from case.serializers.enquiry import (
    CallbackCreateSerializer,
    CallbackSearchSerializer,
    CallbackSerializer,
    CallSerializer,
    ContactSerializer,
    EnquirySearchSerializer,
)
from case.utils import ClerkPaginator, render_react_page
from case.views.auth import (
    CoordinatorOrBetterPermission,
    coordinator_or_better_required,
)
from core.services.enquiry_match import Enquiry, find_client_matches
from webhooks.models import WebflowContact


@api_view(["GET"])
@coordinator_or_better_required
def enquiry_list_page_view(request):
    return render_react_page(request, "Enquiries", "enquiry-list", {})


class EnquiryPaginator(ClerkPaginator):
    page_size = 20


class EnquiryApiViewset(GenericViewSet, ListModelMixin, UpdateModelMixin):
    """
    Lists people who contacted us outside the intake form, and lets staff
    record their follow-up.
    """

    pagination_class = EnquiryPaginator
    permission_classes = [CoordinatorOrBetterPermission]
    # PATCH only: a PUT would need every field, and only one can change.
    http_method_names = ["get", "patch", "head", "options"]

    def get_queryset(self) -> QuerySet:
        queryset = self.queryset.order_by("-created_at").prefetch_related(
            Prefetch(
                "callbacks",
                queryset=Callback.objects.select_related("logged_by").order_by(
                    "-created_at"
                ),
                to_attr="callback_list",
            )
        )
        if self.action == "list":
            serializer = EnquirySearchSerializer(
                data=self.request.query_params, partial=True
            )
            serializer.is_valid(raise_exception=True)
            queryset = queryset.filter(**serializer.validated_data)
        return queryset

    def get_serializer(self, *args, **kwargs):
        # Match the whole page at once rather than querying per row.
        instance = args[0] if args else None
        if instance is not None:
            enquiries = instance if kwargs.get("many") else [instance]
            kwargs["context"] = {
                **self.get_serializer_context(),
                "client_matches": find_client_matches(
                    [self.to_enquiry(e) for e in enquiries]
                ),
            }
        return super().get_serializer(*args, **kwargs)

    def to_enquiry(self, obj) -> Enquiry:
        raise NotImplementedError


class CallApiViewset(EnquiryApiViewset):
    queryset = Call.objects.all()
    serializer_class = CallSerializer

    def to_enquiry(self, obj: Call) -> Enquiry:
        return Enquiry(id=obj.pk, created_at=obj.created_at, phone=obj.phone_number)


class ContactApiViewset(EnquiryApiViewset):
    queryset = WebflowContact.objects.all()
    serializer_class = ContactSerializer

    def to_enquiry(self, obj: WebflowContact) -> Enquiry:
        return Enquiry(
            id=obj.pk, created_at=obj.created_at, phone=obj.phone, email=obj.email
        )


class CallbackApiViewset(GenericViewSet, ListModelMixin, CreateModelMixin):
    """
    Lists and logs the calls staff make back to people who got in touch.
    """

    queryset = Callback.objects.select_related("logged_by").order_by("-created_at")
    permission_classes = [CoordinatorOrBetterPermission]
    # An enquiry's history is short, so it comes back whole.
    pagination_class = None

    def get_serializer_class(self):
        if self.action == "create":
            return CallbackCreateSerializer
        return CallbackSerializer

    def get_queryset(self) -> QuerySet:
        queryset = super().get_queryset()
        if self.action == "list":
            serializer = CallbackSearchSerializer(data=self.request.query_params)
            serializer.is_valid(raise_exception=True)
            queryset = queryset.filter(**serializer.validated_data)
        return queryset

    def perform_create(self, serializer):
        serializer.save(logged_by=self.request.user)
