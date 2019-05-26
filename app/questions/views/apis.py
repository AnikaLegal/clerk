from rest_framework import viewsets

from questions.models import Submission, ImageUpload

from .serializers import SubmissionSerializer, ImageUploadSerializer


class SubmissionViewSet(viewsets.ModelViewSet):
    http_method_names = ("post",)
    serializer_class = SubmissionSerializer
    queryset = Submission.objects.all()


class ImageUploadViewSet(viewsets.ModelViewSet):
    http_method_names = ("post",)
    serializer_class = ImageUploadSerializer
    queryset = ImageUpload.objects.all()
