"""
Questions app API endpoints.
These JSON HTTP APIs are consumed by the frontend app.
"""
from rest_framework import mixins, status, viewsets
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin, ListModelMixin,
                                   UpdateModelMixin)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .models import Question, Script, Submission, Transition
from .serializers import (QuestionSerializer, ScriptSerializer, SubmissionSerializer,
                          TransitionSeializer)


class ScriptViewSet(CreateModelMixin, UpdateModelMixin, ListModelMixin, GenericViewSet):
    """
    List or create scripts
    """

    serializer_class = ScriptSerializer
    queryset = Script.objects.all()


class QuestionViewSet(
    CreateModelMixin, UpdateModelMixin, DestroyModelMixin, ListModelMixin, GenericViewSet
):
    """
    List, create, questions.
    # TODO - we're going to need some pretty slick validation on
             cross-cutting concerns, eg - can't follow a dead question
    # TODO - filter by scripts so we don't pull all questions from DB
    """

    serializer_class = QuestionSerializer
    queryset = Question.objects.prefetch_related('parent_transitions').all()

    def destroy(self, request, *args, **kwargs):
        """
        Delete an existing question, return the deleted question id success.
        """
        question = self.get_object()
        pk = question.pk
        self.perform_destroy(question)
        return Response({'id': pk})


class SubmissionViewSet(CreateModelMixin, ListModelMixin, GenericViewSet):
    """
    List, create, answers.
    # TODO - filter by scripts so we don't pull all questions from DB
    """

    serializer_class = SubmissionSerializer
    queryset = Submission.objects.all()


class TransitionViewSet(
    CreateModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet
):
    """
    Create, update transitions.
    """

    serializer_class = TransitionSeializer
    queryset = Transition.objects.all()

    def create(self, request, *args, **kwargs):
        """
        Create a new transition, return the 'next' question on success.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        transition = serializer.save()
        question_data = QuestionSerializer(transition.next).data
        return Response(question_data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """
        Update an existing transition, return the 'next' question on success.
        """
        transition = self.get_object()
        serializer = self.get_serializer(transition, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        question_data = QuestionSerializer(transition.next).data
        return Response(question_data)

    def destroy(self, request, *args, **kwargs):
        """
        Delete an existing transition, return the 'next' question on success.
        """
        transition = self.get_object()
        question = transition.next
        self.perform_destroy(transition)
        question_data = QuestionSerializer(question).data
        return Response(question_data)
