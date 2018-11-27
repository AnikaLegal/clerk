"""
Questions app API endpoints.
These JSON HTTP APIs are consumed by the frontend app.
"""
from rest_framework import mixins, viewsets

from .models import Question, Script, Submission
from .serializers import (QuestionSerializer, ScriptSerializer,
                          SubmissionSerializer)


class ScriptViewSet(mixins.CreateModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.ListModelMixin,
                    viewsets.GenericViewSet):
    """
    List or create scripts
    """
    serializer_class = ScriptSerializer
    queryset = Script.objects.all()


class QuestionViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    List, create, questions.
    # TODO - we're going to need some pretty slick validation on
             cross-cutting concerns, eg - can't follow a dead question
    # TODO - filter by scripts so we don't pull all questions from DB
    """
    serializer_class = QuestionSerializer
    queryset = Question.objects.prefetch_related('parent_transitions').all()


class SubmissionViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    List, create, answers.
    # TODO - filter by scripts so we don't pull all questions from DB
    """
    serializer_class = SubmissionSerializer
    queryset = Submission.objects.all()
