from rest_framework.decorators import action
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from core.models import FileUpload, Submission
from core.serializers import FileUploadSerializer, SubmissionSerializer


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
        if submission.is_complete:
            # Re-saving a complete submission would queue processing again
            # and create duplicate issues.
            raise SubmittedException()
        # Without these keys process_submission cannot run and, lacking an
        # email, the submission is invisible to abandonment reminders too.
        answers = submission.answers or {}
        missing = [k for k in ("EMAIL", "ISSUES") if not answers.get(k)]
        if missing:
            raise ValidationError(
                {"answers": f"Missing required answers: {', '.join(missing)}"}
            )
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
