from accounts.models import User
from case.middleware import COORDINATOR_GROUPS
from case.serializers import IssueSerializer, UserSerializer
from core.models import Issue
from django.db.models import Q
from django.urls import reverse
from django.utils.timezone import now
from rest_framework import exceptions, serializers
from task.models.request import TaskRequestStatus, TaskRequestType
from task.models.task import Task
from task.models.template import TaskTemplateType

from .actions import TaskRequestSerializer
from .user import TaskListUserSerializer


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


class TaskListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = (
            "id",
            "type",
            "type_display",
            "name",
            "status",
            "status_display",
            "issue",
            "assigned_to",
            "is_open",
            "is_suspended",
            "due_at",
            "closed_at",
            "is_urgent",
            "is_approval_required",
            "is_approval_pending",
            "is_approved",
            "days_open",
            "url",
            "created_at",
            "modified_at",
        )
        read_only_fields = (
            "is_open",
            "is_suspended",
        )

    type_display = serializers.CharField(source="get_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    issue = TaskListIssueSerializer(read_only=True)
    assigned_to = TaskListUserSerializer(read_only=True)
    due_at = serializers.DateField(read_only=True)
    closed_at = serializers.DateTimeField(read_only=True)
    days_open = serializers.IntegerField(read_only=True)
    is_approval_pending = serializers.SerializerMethodField(read_only=True)
    url = serializers.SerializerMethodField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    modified_at = serializers.DateTimeField(read_only=True)

    def get_is_approval_pending(self, obj):
        return (
            obj.requests.filter(type=TaskRequestType.APPROVAL)
            .exclude(status=TaskRequestStatus.DONE)
            .exists()
        )

    def get_url(self, obj):
        return reverse("task-detail", args=(obj.pk,))


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = (
            "id",
            "type",
            "type_display",
            "name",
            "description",
            "status",
            "status_display",
            "issue_id",
            "issue",
            "assigned_to_id",
            "assigned_to",
            "is_open",
            "is_suspended",
            "due_at",
            "closed_at",
            "is_urgent",
            "is_approved",
            "is_approval_required",
            "is_approval_pending",
            "days_open",
            "request",
            "url",
            "created_at",
            "modified_at",
        )
        read_only_fields = (
            "status",
            "is_open",
            "is_suspended",
            "is_approved",
        )

    issue_id = serializers.UUIDField()
    type = serializers.ChoiceField(
        choices=list(TaskTemplateType.choices) + list(TaskRequestType.choices)
    )
    type_display = serializers.CharField(source="get_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    issue = IssueSerializer(read_only=True)
    assigned_to_id = serializers.IntegerField()
    assigned_to = UserSerializer(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    due_at = serializers.DateField(allow_null=True, required=False)
    closed_at = serializers.DateTimeField(read_only=True)
    days_open = serializers.IntegerField(read_only=True)
    request = TaskRequestSerializer(read_only=True)
    is_approval_pending = serializers.SerializerMethodField(read_only=True)

    def get_is_approval_pending(self, obj):
        return (
            obj.requests.filter(type=TaskRequestType.APPROVAL)
            .exclude(status=TaskRequestStatus.DONE)
            .exists()
        )

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

    def validate_due_at(self, value):
        # Due date must be in the future.
        if value and value <= now().date():
            raise exceptions.ValidationError("Due date must be after today's date.")
        return value

    def validate(self, attrs):
        self._check_assigned_to_user_can_access_issue(attrs)
        self._check_issue_has_supervisor_when_approval_required(attrs)
        return attrs

    def _check_assigned_to_user_can_access_issue(self, attrs):
        # Tasks can only be assigned to:
        #
        # - Users with coordinator or greater permissions.
        # - Users assigned as the paralegal on the related case.
        # - Users designated as "system" accounts.
        #
        assigned_to_id = attrs.get("assigned_to_id", None)
        issue_id = attrs.get("issue_id", None)

        if assigned_to_id and issue_id:
            q_filter = Q(id=assigned_to_id) & Q(
                Q(groups__name__in=COORDINATOR_GROUPS)
                | Q(is_superuser=True)
                | Q(is_system_account=True)
            )
            q_filter |= Q(issue__id=issue_id) & Q(issue__paralegal=assigned_to_id)

            if not User.objects.filter(q_filter).exists():
                raise exceptions.ValidationError(
                    {"assigned_to_id": "User does not have access to the case."}
                )

    def _check_issue_has_supervisor_when_approval_required(self, attrs):
        # Tasks can only be set to require approval if there is a supervising
        # lawyer on the case.
        #
        is_approval_required = attrs.get("is_approval_required", None)
        issue_id = attrs.get("issue_id", None)

        if is_approval_required and issue_id:
            if not Issue.objects.filter(id=issue_id, lawyer__isnull=False).exists():
                raise exceptions.ValidationError(
                    {"is_approval_required": "No case supervisor to approve task."}
                )


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
