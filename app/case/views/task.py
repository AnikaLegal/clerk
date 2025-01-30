from core.models.issue import CaseTopic
from django.db.models import Prefetch, Q, QuerySet
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from rest_framework import status
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from task.models.attachment import TaskAttachment
from task.models.task import Task, TaskStatus, TaskTemplateType, TaskType
from task.serializers import (
    TaskAttachmentSerializer,
    TaskCommentSerializer,
    TaskListSerializer,
    TaskSearchSerializer,
    TaskSerializer,
)

from case.utils.react import render_react_page
from case.views.auth import (
    CoordinatorOrBetterPermission,
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
            "my_tasks": [
                ("true", "My tasks"),
                ("false", "All tasks"),
            ],
            "status": TaskStatus.choices,
            "type": TaskTemplateType.choices + TaskType.choices,
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
            "status": TaskStatus.choices,
            "type": TaskTemplateType.choices + TaskType.choices,
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
            # Anyone can try look at the list
            permission_classes = [IsAuthenticated]
        else:
            # But for other stuff you need to be a coordinator+ or have object permission
            permission_classes = [
                CoordinatorOrBetterPermission | ParalegalOrBetterObjectPermission
            ]
        return [p() for p in permission_classes]

    def get_queryset(self):
        user = self.request.user

        queryset = Task.objects.all()
        queryset = Task.annotate_with_days_open(queryset)
        queryset = queryset.select_related("issue", "assigned_to")
        queryset = queryset.prefetch_related("assigned_to__groups")

        if self.action == "retrieve":
            queryset = queryset.prefetch_related("comments").prefetch_related(
                Prefetch(
                    "attachments",
                    queryset=TaskAttachment.objects.filter(comment_id__isnull=True),
                )
            )
        elif self.action == "list":
            queryset = queryset.order_by("-is_urgent", "due_at", "-days_open")
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

    def search_queryset(self, queryset: QuerySet[Task]) -> QuerySet[Task]:
        """
        Filter queryset by search terms in query params.
        """
        serializer = TaskSearchSerializer(data=self.request.query_params, partial=True)
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
                elif key == "my_tasks":
                    if value:
                        queryset = queryset.filter(Q(assigned_to=self.request.user))
                else:
                    queryset = queryset.filter(**{key: value})

        return queryset

    @action(
        detail=True, methods=["GET", "POST"], serializer_class=TaskCommentSerializer
    )
    def comments(self, request, pk):
        """
        Task comments.
        """
        task = self.get_object()

        if request.method == "GET":
            queryset = task.comments.all()
            queryset = queryset.select_related("creator")
            queryset = queryset.order_by("created_at")
            data = self.get_serializer(queryset, many=True).data
            return Response(data)
        else:
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
