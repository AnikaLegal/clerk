"""
Questions app serializers.
Used to validate API requests and convert our models to/from JSON.
"""
from rest_framework import serializers

from .models import Question, Script, Submission, Transition


class ScriptSerializer(serializers.ModelSerializer):
    """
    A script, which contains a series of questions
    """
    class Meta:
        model = Script
        read_only_fields = ('questions', 'modified_at')
        fields = ('id', 'name', 'questions', 'modified_at')


class TransitionSeializer(serializers.ModelSerializer):
    """
    A transition that leads from one question to the next
    """
    class Meta:
        model = Question
        read_only_fields = ('modified_at',)
        fields = (
            'id',
            'previous',
            'next',
            'condition',
            'variable',
            'value',
            'modified_at',
        )


class QuestionSerializer(serializers.ModelSerializer):
    """
    A single question, part of a script
    """
    class Meta:
        model = Question
        read_only_fields = ('modified_at',)
        fields = (
            'id',
            'name',
            'is_first',
            'prompt',
            'field_type',
            'parent_transitions',
            'modified_at',
        )

    parent_transitions = TransitionSeializer(many=True)


class AnswerSerializer(serializers.Serializer):
    """
    A single answer to a question
    """
    question_id = serializers.IntegerField(min_value=0)
    question_name = serializers.CharField(min_length=1, max_length=256)
    question_prompt = serializers.CharField(min_length=1, max_length=256)
    field_type = serializers.CharField(min_length=1, max_length=32)


class SubmissionSerializer(serializers.ModelSerializer):
    """
    A set of answers for a script
    """
    class Meta:
        model = Submission
        read_only_fields = ('modified_at',)
        fields = (
            'script',
            'modified_at',
            'answers',
        )

    answers = AnswerSerializer(many=True)
