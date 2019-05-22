from rest_framework import viewsets

from questions.models import Submission

from .serializers import SubmissionSerializer


class SubmissionViewSet(viewsets.ModelViewSet):
    http_method_names = ('post',)
    serializer_class = SubmissionSerializer
    queryset = Submission.objects.all()
