from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets

from questions.models import Submission

from .serializers import SubmissionSerializer


# FIXME: Remove CSRF exempt decorator once users can log in and fetch a token.
@csrf_exempt
class SubmissionViewSet(viewsets.ModelViewSet):
    http_method_names = ('post',)
    serializer_class = SubmissionSerializer
    queryset = Submission.objects.all()
