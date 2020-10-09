from django.db.models import Q
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.exceptions import APIException

from core.models import Client, Person, FileUpload, Tenancy, Issue
from core.serializers import (
    ClientSerializer,
    PersonSerializer,
    FileUploadSerializer,
    TenancySerializer,
    IssueSerializer,
)


class ClientViewSet(
    GenericViewSet, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin
):
    prefetch = (
        "issue_set__fileupload_set",
        "tenancy_set__agent",
        "tenancy_set__landlord",
    )
    queryset = Client.objects.prefetch_related(*prefetch).all()
    serializer_class = ClientSerializer

    def update(self, request, *args, **kwargs):
        client = self.get_object()
        has_submitted_issue = client.issue_set.filter(is_submitted=True).exists()
        if has_submitted_issue:
            raise IssueSubmittedException()

        return super().update(request, *args, **kwargs)


class PersonViewSet(GenericViewSet, CreateModelMixin, UpdateModelMixin):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer

    def update(self, request, *args, **kwargs):
        person = self.get_object()
        # Assume each person has 1 tenancy which has 1 client
        # This may not always be true.
        tenancy = Tenancy.objects.filter(Q(agent=person) | Q(landlord=person)).first()
        if tenancy:
            has_submitted_issue = tenancy.client.issue_set.filter(
                is_submitted=True
            ).exists()
            if has_submitted_issue:
                raise IssueSubmittedException()

        return super().update(request, *args, **kwargs)


class UploadViewSet(GenericViewSet, CreateModelMixin):
    queryset = FileUpload.objects.all()
    serializer_class = FileUploadSerializer


class TenancyViewSet(GenericViewSet, CreateModelMixin, UpdateModelMixin):
    queryset = Tenancy.objects.all()
    serializer_class = TenancySerializer

    def update(self, request, *args, **kwargs):
        tenancy = self.get_object()
        has_submitted_issue = tenancy.client.issue_set.filter(
            is_submitted=True
        ).exists()
        if has_submitted_issue:
            raise IssueSubmittedException()

        return super().update(request, *args, **kwargs)


class IssueViewSet(GenericViewSet, CreateModelMixin, UpdateModelMixin):
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer

    def update(self, request, *args, **kwargs):
        issue = self.get_object()
        if issue.is_submitted:
            raise IssueSubmittedException()

        return super().update(request, *args, **kwargs)


class IssueSubmittedException(APIException):
    status_code = 403
    default_detail = "Cannot modify a submitted case."
    default_code = "issue_submitted"
