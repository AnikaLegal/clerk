"""
Questions app data models.
"""
from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils import timezone


class FieldTypes:
    """
    The set of possible field data types for a question
    In the future, consider adding:
    email, multiple choice, date  single choice, info  more?
    """

    TEXT = 'TEXT'
    NUMBER = 'NUMBER'
    BOOLEAN = 'BOOLEAN'


class ConditionTypes:
    """
    The set of possible transition conditions,
    In the future, consider adding is not, equals, ??
    """

    EQUALS = 'EQUALS'


class TimestampedModel(models.Model):
    """
    Abstract base class that implements timestamps on create / update.
    """

    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.modified_at = timezone.now()
        super().save(*args, **kwargs)


class Script(TimestampedModel):
    """
    A series of questions used to collect data from a user.
    Todo: add versions
    """

    # Internal name for this questionnaire script.
    name = models.CharField(max_length=64)
    # The first question to be asked.
    first_question = models.ForeignKey(
        'questions.Question',
        on_delete=models.SET_NULL,
        related_name='first_for',
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name


class Question(TimestampedModel):
    """
    A single question asked in a script
    todo: options, hint
    """

    TYPE_CHOICES = (
        (FieldTypes.TEXT, 'Text'),
        (FieldTypes.NUMBER, 'Number'),
        (FieldTypes.BOOLEAN, 'Yes / No'),
    )
    # The questionnaire script that this question belongs to.
    script = models.ForeignKey(Script, on_delete=models.CASCADE, related_name='questions')
    # A description of the question.
    name = models.CharField(max_length=256)
    # The text presented to the user.
    prompt = models.CharField(max_length=256)
    # The data type required for the answer.
    field_type = models.CharField(max_length=32, choices=TYPE_CHOICES)

    def __str__(self):
        return f'{self.name} of {self.script.name}'


class Transition(TimestampedModel):
    """
    A conditional jump from one question to the next.
    """

    CONDITION_CHOICES = ((ConditionTypes.EQUALS, 'equals'),)
    # The question that precedes the transition
    previous = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='child_transitions'
    )
    # The question that follows the transition
    next = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='parent_transitions'
    )
    # The condition used to figure out whether we should follow this transition
    condition = models.CharField(
        max_length=32, choices=CONDITION_CHOICES, null=True, blank=True
    )
    # The answer variable used to evaluate the condition
    variable = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='variables',
        null=True,
        blank=True,
    )
    # The value used to evaluate the condition
    value = models.CharField(max_length=256, null=True, blank=True)

    def __str__(self):
        return f'{self.previous.name} to {self.next.name}'


class Submission(TimestampedModel):
    """
    A set of answers to a Script
    I'm not sure the best way to store this for now,
    so let's just dump it in a JSON and figure it our later #YOLO.
    """

    script = models.ForeignKey(
        Script, on_delete=models.CASCADE, related_name='submissions'
    )
    answers = JSONField(encoder=DjangoJSONEncoder)

    def __str__(self):
        return f'{self.script.name} on {self.modified_at}'
