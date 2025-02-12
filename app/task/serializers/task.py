from accounts.models import User
from case.middleware import COORDINATOR_GROUPS
from case.serializers import IssueSerializer, UserSerializer
from django.db.models import Q
from django.urls import reverse
from rest_framework import exceptions, serializers
from task.models import Task
from task.models.task import TaskType


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
            "is_open",
            "is_suspended",
            "created_at",
            "due_at",
            "closed_at",
            "is_urgent",
            "is_approval_required",
            "days_open",
            "url",
        )
        read_only_fields = (
            "status",
            "is_open",
            "is_suspended",
            "is_approved",
        )

    issue_id = serializers.UUIDField()
    issue = IssueSerializer(read_only=True)
    assigned_to_id = serializers.IntegerField()
    assigned_to = UserSerializer(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    due_at = serializers.DateField(allow_null=True, required=False)
    closed_at = serializers.DateTimeField(read_only=True)
    days_open = serializers.IntegerField(read_only=True)

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
        if request and not request.user.is_lawyer_or_better:
            raise exceptions.PermissionDenied()
        return value

    def validate(self, attrs):
        # Tasks can only be assigned to:
        # - Users with coordinator or greater permissions.
        # - Users assigned as the paralegal on the related case.
        # - Users designated as "system" accounts.
        assigned_to_id = attrs.get("assigned_to_id", None)
        if assigned_to_id:
            q_filter = Q(id=assigned_to_id) & Q(
                Q(groups__name__in=COORDINATOR_GROUPS)
                | Q(is_superuser=True)
                | Q(is_system_account=True)
            )
            issue_id = attrs.get("issue_id", None)
            if issue_id:
                q_filter |= Q(issue__id=issue_id) & Q(issue__paralegal=assigned_to_id)

            if not User.objects.filter(q_filter).exists():
                raise exceptions.ValidationError(
                    {"assigned_to_id": "User does not have access to the case."}
                )

        return attrs


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
        )
        extra_kwargs = {f: {"required": False} for f in fields}

    issue__topic = serializers.CharField(required=False)
    # Special case searches.
    q = serializers.CharField(required=False)  # General query.
