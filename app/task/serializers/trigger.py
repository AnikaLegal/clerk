from core.models.issue_event import EventType
from django.urls import reverse
from rest_framework import serializers
from task.models import TaskTemplate, TaskTrigger

from .template import TaskTemplateSerializer


class TaskTriggerSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskTrigger
        fields = (
            "id",
            "name",
            "topic",
            "event",
            "event_stage",
            "tasks_assignment_role",
            "templates",
            "created_at",
            "url",
        )

    templates = TaskTemplateSerializer(many=True)
    created_at = serializers.DateTimeField(read_only=True)
    url = serializers.SerializerMethodField(read_only=True)

    def get_url(self, obj):
        return reverse("template-task-detail", args=(obj.pk,))

    def create(self, validated_data):
        templates_data = validated_data.pop("templates")
        trigger = TaskTrigger.objects.create(**validated_data)
        for data in templates_data:
            TaskTemplate.objects.create(trigger=trigger, **data)
        return trigger

    def update(self, instance, validated_data):
        to_add = []
        to_delete = []
        to_update = []

        # Determine whether we need to add, delete or update any templates based
        # on the incoming nested templates data.
        for data in validated_data.pop("templates"):
            if "id" in data:
                to_update.append(data)
            else:
                to_add.append(data)

        ids = {x["id"] for x in to_update}
        for template in instance.templates.all():
            if template.id not in ids:
                to_delete.append(template.id)

        # Do the required operations.
        for id in to_delete:
            instance.templates.all().get(id=id).delete()

        for data in to_add:
            TaskTemplate.objects.create(trigger=instance, **data)

        for data in to_update:
            template = instance.templates.all().get(id=data["id"])
            for attr, value in data.items():
                setattr(template, attr, value)
            template.save()

        return super().update(instance, validated_data)

    def validate(self, attrs):
        event = attrs.get("event")
        event_stage = attrs.get("event_stage")
        if event == EventType.STAGE and not event_stage:
            raise serializers.ValidationError(
                {"event_stage": self.fields["event_stage"].error_messages["required"]}
            )

        return attrs
