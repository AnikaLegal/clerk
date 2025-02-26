from accounts.models import CaseGroups
from core.models.issue import CaseTopic
from django.db.models import Prefetch, Q, QuerySet
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from rest_framework import status
from rest_framework.decorators import action, api_view
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from task.helpers import get_coordinators_user
from task.models import TaskAttachment
from task.models.task import RequestTaskType, Task, TaskStatus, TaskType
from task.models.event import TaskEventType
from task.serializers import (
    TaskActivitySerializer,
    TaskAttachmentSerializer,
    TaskCommentSerializer,
    TaskListSerializer,
    TaskSearchSerializer,
    TaskSerializer,
)
from task.serializers.actions import (
    TaskApprovalSerializer,
    TaskCreateRequestSerializer,
    TaskStatusChangeSerializer,
)

from case.utils.react import render_react_page
from case.views.auth import (
    CoordinatorOrBetterPermission,
    LawyerOrBetterPermission,
    ParalegalOrBetterObjectPermission,
    paralegal_or_better_required,
)

# TODO:
# - review permissions.


@api_view(["GET"])
@paralegal_or_better_required
def task_list_page_view(request):
    context = {
        "choices": {
            "case_topic": CaseTopic.CHOICES,
            "is_open": [
                ("true", "Open"),
                ("false", "Closed"),
            ],
            "status": TaskStatus.choices,
            "type": TaskType,
        },
    }
    return render_react_page(request, "Tasks", "task-list", context)


@api_view(["GET"])
@paralegal_or_better_required
def task_detail_page_view(request, pk):
    if not Task.objects.filter(pk=pk).exists():
        raise Http404()

    context = {
        "choices": {
            "event_type": TaskEventType.choices,
            "status": TaskStatus.choices,
            "type": TaskType,
        },
        "status": {
            "stopped": TaskStatus.NOT_STARTED,
            "started": TaskStatus.IN_PROGRESS,
            "finished": TaskStatus.DONE,
            "cancelled": TaskStatus.NOT_DONE,
        },
        "task_pk": pk,
        "list_url": reverse("task-list"),
    }
    return render_react_page(request, "Task", "task-detail", context)


class TaskApiViewset(ModelViewSet):
    serializer_class = TaskSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return TaskListSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action == "list":
            permission_classes = [IsAuthenticated]
        elif self.action == "approval":
            permission_classes = [LawyerOrBetterPermission]
        elif (
            self.action == "retrieve"
            or self.action == "activity"
            or self.action == "attachments"
            or self.action == "attachment_delete"
            or self.action == "comments"
            or self.action == "status_change"
            or self.action == "request"
        ):
            permission_classes = [
                CoordinatorOrBetterPermission | ParalegalOrBetterObjectPermission
            ]
        else:
            permission_classes = [CoordinatorOrBetterPermission]

        return [p() for p in permission_classes]

    def get_queryset(self):
        user = self.request.user

        queryset = Task.objects.all()
        queryset = Task.annotate_with_days_open(queryset)
        queryset = queryset.select_related("issue", "assigned_to")
        queryset = queryset.prefetch_related("assigned_to__groups")

        if self.action == "retrieve":
            queryset = queryset.prefetch_related("activities").prefetch_related(
                Prefetch(
                    "attachments",
                    queryset=TaskAttachment.objects.filter(comment_id__isnull=True),
                )
            )
        elif self.action == "list":
            queryset = self.sort_queryset(queryset)
            queryset = self.search_queryset(queryset)

        # Permissions.
        if user.is_paralegal:
            queryset = queryset.filter(Q(assigned_to=user))
            # Double check: Even if they are assigned to a task, paralegals
            # should only be able to see the tasks related to cases of which
            # they are the assigned paralegal.
            queryset = queryset.filter(issue__paralegal=user)
        elif not user.is_coordinator_or_better:
            # No permissions if you're not a paralegal or coordinator+.
            queryset = queryset.none()

        return queryset

    def sort_queryset(self, queryset: QuerySet[Task]) -> QuerySet[Task]:
        return queryset.order_by("-is_urgent", "due_at", "-days_open")

    def search_queryset(self, queryset: QuerySet[Task]) -> QuerySet[Task]:
        """
        Filter queryset by search terms in query params.
        """
        request = self.request
        serializer = TaskSearchSerializer(data=request.query_params, partial=True)
        serializer.is_valid(raise_exception=True)
        terms = serializer.validated_data

        for key, value in terms.items():
            if value is not None:
                if key == "q":
                    # Run free text search query
                    parts = value.split(" ")
                    query = None
                    for part in parts:
                        q_filter = (
                            Q(name__icontains=part)
                            | Q(assigned_to__first_name__icontains=part)
                            | Q(assigned_to__last_name__icontains=part)
                            | Q(assigned_to__email__icontains=part)
                            | Q(issue__fileref__icontains=part)
                        )
                        if query:
                            query |= q_filter
                        else:
                            query = q_filter
                    queryset = queryset.filter(query)
                elif key == "assigned_to":
                    q_filter = Q(assigned_to=value)
                    # Coordinator users are also displayed tasks assigned to
                    # coordinators when filtering by their own tasks.
                    if value.groups.filter(name=CaseGroups.COORDINATOR).exists():
                        coordinators_user = get_coordinators_user()
                        q_filter |= Q(assigned_to=coordinators_user)
                    queryset = queryset.filter(q_filter)
                else:
                    queryset = queryset.filter(**{key: value})

        return queryset

    @action(
        detail=True,
        methods=["GET"],
        serializer_class=TaskActivitySerializer,
    )
    def activity(self, request, pk):
        """
        Task activity.
        """
        task = self.get_object()

        queryset = task.activities.all()
        queryset = queryset.select_related("content_type")
        queryset = queryset.order_by("-created_at")
        data = self.get_serializer(queryset, many=True).data
        return Response(data)

    @action(detail=True, methods=["POST"], serializer_class=TaskCommentSerializer)
    def comments(self, request, pk):
        """
        Task comments.
        """
        task = self.get_object()
        data = {
            **request.data,
            "task_id": task.pk,
        }
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True, methods=["GET", "POST"], serializer_class=TaskAttachmentSerializer
    )
    def attachments(self, request, pk):
        """
        task attachments.
        """
        task = self.get_object()

        if request.method == "GET":
            queryset = task.attachments.all()
            queryset = queryset.order_by("created_at")
            data = self.get_serializer(queryset, many=True).data
            return Response(data)
        else:
            request.data["task_id"] = task.pk
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=["DELETE"],
        url_path="attachments/(?P<attachment_id>[0-9]+)",
    )
    def attachment_delete(self, request, pk, attachment_id):
        task = self.get_object()
        attachment = get_object_or_404(task.attachments, pk=attachment_id)
        attachment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["PATCH"], serializer_class=TaskStatusChangeSerializer)
    def status_change(self, request, pk):
        task = self.get_object()

        serializer = self.get_serializer(instance=task, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        data = TaskSerializer(instance=task).data
        return Response(data)

    @action(detail=True, methods=["POST"], serializer_class=TaskCreateRequestSerializer)
    def request(self, request, pk):
        task = self.get_object()

        # Disallow approval requests if there is already one pending.
        type = request.data.get("type", None)
        if type == RequestTaskType.APPROVAL and task.is_approval_pending:
            raise ApprovalAlreadyPendingException()

        data = {
            **request.data,
            "issue_id": task.issue_id,
            "requesting_task_id": task.pk,
        }
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        task.is_approval_pending = True
        task.save()

        # NOTE: We respond 200 OK with the requesting task, not 203 CREATED
        # with the created task, as:
        #
        # - the user does not necessarily have access to the created task
        # - it makes refreshing the client-side easier
        #
        # Conceptually you can consider this an "update" to the requesting task
        # that happens to have the side effect of creating a new task.
        data = TaskSerializer(instance=task).data
        return Response(data)

    @action(detail=True, methods=["PATCH"], serializer_class=TaskApprovalSerializer)
    def approval(self, request, pk):
        task = self.get_object()
        if task.type != RequestTaskType.APPROVAL:
            raise NotApprovalException()

        serializer = self.get_serializer(instance=task, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        data = TaskSerializer(instance=task).data
        return Response(data)


class ApprovalAlreadyPendingException(APIException):
    status_code = 403
    default_code = "approval_already_pending"
    default_detail = "An approval has already been requested and is pending."

class NotApprovalException(APIException):
    status_code = 403
    default_code = "task_not_approval_request"
    default_detail = "Cannot update a task that is not an approval request."