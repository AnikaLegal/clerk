from case.serializers import IssueSerializer, UserSerializer
from core.models.issue_event import EventType
from django.urls import reverse
from rest_framework import serializers, exceptions


from .models import Task, TaskAttachment, TaskComment, TaskTemplate, TaskTrigger
from .models.task import TaskStatus, TaskType


class TaskTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskTemplate
        fields = (
            "id",
            "type",
            "name",
            "description",
            "due_in",
            "is_urgent",
            "is_approval_required",
        )

    id = serializers.IntegerField(required=False)


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


class TaskListIssueSerializer(IssueSerializer):
    class Meta:
        model = IssueSerializer.Meta.model
        fields = (
            "id",
            "fileref",
            "topic",
            "url",
        )

    # Bypass the parent method as it references a field we do not include.
    def get_fields(self, *args, **kwargs):
        return super(IssueSerializer, self).get_fields(*args, **kwargs)


class TaskListUserSerializer(UserSerializer):
    class Meta:
        model = UserSerializer.Meta.model
        read_only_fields = UserSerializer.Meta.read_only_fields
        fields = (
            "id",
            "full_name",
            "url",
        )


class TaskListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = (
            "id",
            "type",
            "name",
            "status",
            "issue",
            "assigned_to",
            "is_open",
            "is_suspended",
            "created_at",
            "due_at",
            "closed_at",
            "is_urgent",
            "is_approval_required",
            "is_approved",
            "days_open",
            "url",
        )
        read_only_fields = (
            "is_open",
            "is_suspended",
        )

    issue = TaskListIssueSerializer(read_only=True)
    assigned_to = TaskListUserSerializer(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    due_at = serializers.DateField(read_only=True)
    closed_at = serializers.DateTimeField(read_only=True)
    days_open = serializers.IntegerField(read_only=True)
    url = serializers.SerializerMethodField(read_only=True)

    def get_url(self, obj):
        return reverse("task-detail", args=(obj.pk,))


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = (
            "id",
            "type",
            "name",
            "description",
            "status",
            "issue_id",
            "issue",
            "assigned_to_id",
            "assigned_to",
            "related_task_id",
            "is_open",
            "is_suspended",
            "created_at",
            "due_at",
            "closed_at",
            "is_urgent",
            "is_approval_required",
            "is_approved",
            "days_open",
            "url",
            "is_approval_request",
            "is_question",
        )
        read_only_fields = (
            "is_open",
            "is_suspended",
        )

    issue_id = serializers.UUIDField(write_only=True)
    issue = IssueSerializer(read_only=True)
    assigned_to_id = serializers.IntegerField(write_only=True)
    assigned_to = UserSerializer(read_only=True)
    related_task_id = serializers.IntegerField(allow_null=True, required=False)
    created_at = serializers.DateTimeField(read_only=True)
    due_at = serializers.DateField(allow_null=True, required=False)
    closed_at = serializers.DateTimeField(read_only=True)
    days_open = serializers.IntegerField(read_only=True)

    is_approval_request = serializers.SerializerMethodField(read_only=True)
    is_question = serializers.SerializerMethodField(read_only=True)

    def get_is_approval_request(self, obj):
        return obj.type == TaskType.APPROVAL_REQUEST

    def get_is_question(self, obj):
        return obj.type == TaskType.QUESTION

    def create(self, validated_data):
        # Paralegals can only create approval requests or questions.
        request = self.context.get("request", None)
        if request and request.user.is_paralegal:
            type = validated_data.get("type", None)
            if type is None or type not in [
                TaskType.APPROVAL_REQUEST,
                TaskType.QUESTION,
            ]:
                raise exceptions.PermissionDenied()
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Paralegals can only change the task status.
        request = self.context.get("request", None)
        if request and request.user.is_paralegal:
            keys = [x for x in validated_data.keys() if x not in ["status"]]
            if len(keys) > 0:
                raise exceptions.PermissionDenied()
        return super().update(instance, validated_data)

    def to_internal_value(self, data):
        # Convert empty strings to null for date field. This is just a
        # convenience so we don't have to do it on the frontend.
        for field in ("due_at",):
            if field in data and data[field] == "":
                data[field] = None
        return super().to_internal_value(data)

    def validate_is_approval_required(self, value):
        # Only lawyers can adjust task approvals.
        request = self.context.get("request", None)
        if request and not request.user.is_lawyer:
            raise exceptions.PermissionDenied()
        return value

    def validate_is_approved(self, value):
        # Only lawyers can adjust task approvals.
        request = self.context.get("request", None)
        if request and not request.user.is_lawyer:
            raise exceptions.PermissionDenied()
        return value

    def validate_status(self, value):
        # Only lawyers can finish a task when approval is required but not yet
        # given.
        request = self.context.get("request", None)
        if request and not request.user.is_lawyer:
            instance: Task | None = self.instance
            if (
                value in [TaskStatus.DONE, TaskStatus.NOT_DONE]
                and instance
                and instance.is_approval_required
                and not instance.is_approved
            ):
                raise exceptions.PermissionDenied(detail="Approval is required")
        return value


class TaskSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = (
            "type",
            "name",
            "status",
            "is_open",
            "is_suspended",
            "is_urgent",
            "issue",
            "assigned_to",
            "issue__topic",
            "q",
            "my_tasks",
        )
        extra_kwargs = {f: {"required": False} for f in fields}

    issue__topic = serializers.CharField(required=False)
    # Special case searches.
    q = serializers.CharField(required=False)  # General query.
    my_tasks = serializers.BooleanField(required=False)


class TaskCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskComment
        fields = (
            "id",
            "task_id",
            "creator_id",
            "creator",
            "created_at",
            "type",
            "text",
        )

    task_id = serializers.IntegerField()
    creator_id = serializers.IntegerField(allow_null=True, required=False)
    creator = TaskListUserSerializer(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)


class TaskAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskAttachment
        fields = (
            "id",
            "task_id",
            "comment_id",
            "content_type",
            "created_at",
            "file",
            "name",
            "url",
        )

    task_id = serializers.IntegerField()
    comment_id = serializers.IntegerField(allow_null=True)
    content_type = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    file = serializers.FileField(write_only=True)
    name = serializers.CharField(source="file.name", read_only=True)
    url = serializers.URLField(source="file.url", read_only=True)

    def create(self, validated_data):
        file = validated_data["file"]
        data = {
            **validated_data,
            "content_type": file.content_type,
        }
        return super().create(data)
