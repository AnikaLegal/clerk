from rest_framework import mixins, viewsets

from .models import Questionnaire, Question, Transition, Submission
from .serializers import QuestionnaireSerializer, QuestionSerializer, ParentTransitionSeializer, SubmissionSerializer

# ListModelMixin, Retrive... Create..., Delete... viewsets.GenericViewSet


class WooViewSet(mixins.CreateModelMixin,
                     viewsets.GenericViewSet):
    """
    create:
    Create an Woo if valid campaign exists.
    """
    serializer_class = WooSerializer
    queryset = Woo.objects.all()


class ZZZZtViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    """
    serializer_class = ZZZ
    queryset = (
        ZZ.objects
        .all()
    )
