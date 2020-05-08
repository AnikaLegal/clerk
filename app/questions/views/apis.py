from rest_framework import mixins, status, viewsets
from rest_framework.response import Response

from questions.models import FileUpload, ImageUpload, Submission

from .serializers import FileUploadSerializer, ImageUploadSerializer, SubmissionSerializer


class SubmissionViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
):
    http_method_names = ("get", "post", "patch")
    serializer_class = SubmissionSerializer
    queryset = Submission.objects.all()

    def update(self, request, *args, **kwargs):
        submission = self.get_object()
        if submission.complete:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            return super().update(request, *args, **kwargs)


class ImageUploadViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    http_method_names = ("post",)
    serializer_class = ImageUploadSerializer
    queryset = ImageUpload.objects.all()


class FileUploadViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    http_method_names = ("post",)
    serializer_class = FileUploadSerializer
    queryset = FileUpload.objects.all()
