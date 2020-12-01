from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.exceptions import APIException
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import FileUpload, Submission
from core.serializers import (
    SubmissionSerializer,
    FileUploadSerializer,
)


class UploadViewSet(GenericViewSet, CreateModelMixin):
    """
    An endpoint for questionnaire users to update
    """

    queryset = FileUpload.objects.all()
    serializer_class = FileUploadSerializer


class SubmissionViewSet(
    GenericViewSet, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin
):
    """
    An endpoint for questionnaire users to get/create/update their submission, and then submit it.
    """

    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer

    @action(detail=True, methods=["post"])
    def submit(self, request, *args, **kwargs):
        submission = self.get_object()
        submission.is_complete = True
        submission.save()
        return Response({}, status=200)

    def retrieve(self, request, *args, **kwargs):
        submission = self.get_object()
        if submission.is_complete:
            raise SubmittedException()

        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        submission = self.get_object()
        if submission.is_complete:
            raise SubmittedException()

        return super().update(request, *args, **kwargs)


class SubmittedException(APIException):
    status_code = 403
    default_detail = "Cannot modify a submitted case."
    default_code = "already_submitted"
