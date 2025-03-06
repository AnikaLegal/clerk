from django.db import transaction
from rest_framework import serializers
from task.models import TaskRequest
from task.models.request import TaskRequestType, TaskRequestStatus
from task.models.task import Task, TaskStatus
from task.serializers.user import TaskListUserSerializer


class TaskRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskRequest
        fields = (
            "id",
            "type",
            "from_task_id",
            "from_task_url",
            "from_user",
            "to_task_id",
            "to_task_url",
            "to_user",
            "status",
            "is_approved",
            "to_comment",
        )
        read_only_fields = ("task_id", "type")

    status = serializers.ChoiceField(choices=TaskRequestStatus.choices)
    from_task_url = serializers.SerializerMethodField(read_only=True)
    from_user = TaskListUserSerializer(read_only=True)

    to_task_url = serializers.SerializerMethodField(read_only=True)
    to_user = TaskListUserSerializer(source="to_task.assigned_to", read_only=True)

    def get_from_task_url(self, obj):
        return obj.from_task.url

    def get_to_task_url(self, obj):
        return obj.to_task.url

    @transaction.atomic
    def update(self, instance, validated_data):
        status = validated_data.get("status", None)
        if status:
            to_task = instance.to_task
            to_task.status = (
                TaskStatus.DONE
                if status == TaskRequestStatus.DONE
                else TaskStatus.NOT_STARTED
            )
            to_task.save()

        is_approved = validated_data.get("is_approved", None)
        if is_approved is not None:
            from_task = instance.from_task
            from_task.is_approved = is_approved
            from_task.save()

        return super().update(instance, validated_data)


class TaskCreateRequestSerializer(serializers.Serializer):
    class Meta:
        fields = (
            "task_id",
            "issue_id",
            "type",
            "from_user_id",
            "to_user_id",
            "name",
            "comment",
        )

    task_id = serializers.IntegerField()
    issue_id = serializers.UUIDField()
    type = serializers.ChoiceField(choices=TaskRequestType.choices)
    from_user_id = serializers.IntegerField()
    to_user_id = serializers.IntegerField()
    name = serializers.CharField()
    comment = serializers.CharField()

    @transaction.atomic
    def create(self, validated_data):
        task_id = validated_data["task_id"]
        issue_id = validated_data["issue_id"]
        type = validated_data["type"]
        from_user_id = validated_data["from_user_id"]
        to_user_id = validated_data["to_user_id"]
        name = validated_data["name"]
        comment = validated_data["comment"]

        to_task = Task.objects.create(
            issue_id=issue_id,
            type=type,
            assigned_to_id=to_user_id,
            name=name,
            description=comment,
        )
        TaskRequest.objects.create(
            type=type,
            from_task_id=task_id,
            from_user_id=from_user_id,
            to_task=to_task,
            to_user_id=to_user_id,
            from_comment=comment,
        )

        return validated_data
