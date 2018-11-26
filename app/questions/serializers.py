from rest_framework import serializers

from .models import Questionnaire, Question, Transition, Submission


class QuestionnaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = Questionnaire
        read_only_fields = ('modified_at',)
        fields = ('id', 'name', 'questions', 'modified_at')


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        read_only_fields = ('modified_at',)
        fields = (
            'id',
            'name',
            'prompt',
            'field_type',
            'parent_transitions',
            'modified_at',
        )


class ParentTransitionSeializer(serializers.ModelSerializer):
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


class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        read_only_fields = ('modified_at',)
        fields = (
            'questionnaire',
            'modified_at',
            'answers',
        )

    answers = AnswerSerializer(many=True)


class AnswerSerializer(serializers.Serializer):
    question_id = serializers.IntegerField(min_value=0)
    question_name = serializers.CharField(min_length=1, max_length=256)
    question_prompt = serializers.CharField(min_length=1, max_length=256)
    field_type = serializers.CharField(min_length=1, max_length=32)
    answer = serializers.CharField(min_length=1, max_length=1024)
