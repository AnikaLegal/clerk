"""
Questions app  model factories.
We can use these to easily create test data.
"""
import factory

from .models import FieldTypes, Question, Script, Submission, Transition


class ScriptFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Script

    name = factory.Faker('sentence')


class QuestionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Question

    script = factory.SubFactory(Script)
    name = factory.Faker('sentence')
    prompt = factory.Faker('sentence')
    field_type = FieldTypes.TEXT


class TransitionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Transition

    previous = factory.SubFactory(Question)
    next = factory.SubFactory(Question)


class Submission(factory.django.DjangoModelFactory):
    class Meta:
        model = Submission

    script = factory.SubFactory(Script)

    @factory.lazy_attribute
    def answers(self):
        # TODO
        return {}
