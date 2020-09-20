from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, UpdateModelMixin

from core.models import Client, Person, FileUpload, Tenancy, Submission
from core.serializers import (
    ClientSerializer,
    PersonSerializer,
    FileUploadSerializer,
    TenancySerializer,
    SubmissionSerializer,
)


class ClientViewSet(
    GenericViewSet, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin
):
    prefetch = (
        "submission_set__fileupload_set",
        "tenancy_set__agent",
        "tenancy_set__landlord",
    )
    queryset = Client.objects.prefetch_related(*prefetch).all()
    serializer_class = ClientSerializer


class PersonViewSet(GenericViewSet, CreateModelMixin):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer


class UploadViewSet(GenericViewSet, CreateModelMixin):
    queryset = FileUpload.objects.all()
    serializer_class = FileUploadSerializer


class TenancyViewSet(GenericViewSet, CreateModelMixin, UpdateModelMixin):
    queryset = Tenancy.objects.all()
    serializer_class = TenancySerializer


class SubmissionViewSet(GenericViewSet, CreateModelMixin, UpdateModelMixin):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
