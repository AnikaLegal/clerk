from rest_framework.viewsets import ModelViewSet
from rest_framework_serializer_extensions.views import SerializerExtensionsAPIViewMixin
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, QuerySet
from django.urls import reverse
from django.http import Http404

from case.views.auth import (
    paralegal_or_better_required,
    CoordinatorOrBetterPermission,
    ParalegalOrBetterObjectPermission,
)
from case.utils.react import render_react_page
from core.models.issue import CaseTopic
from task.models.task import Task, TaskType, TaskStatus
from task.serializers import TaskSerializer, TaskSearchSerializer

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
            "type": TaskType.choices,
        }
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
            "type": TaskType.choices,
        },
        "task_pk": pk,
        "list_url": reverse("task-list"),
    }
    return render_react_page(request, "Task", "task-detail", context)


class TaskApiViewset(SerializerExtensionsAPIViewMixin, ModelViewSet):
    serializer_class = TaskSerializer
    extensions_query_params_enabled = False

    def get_extensions_mixin_context(self):
        context = super(TaskApiViewset, self).get_extensions_mixin_context()
        context["expand"] = {"issue", "owner", "assigned_to"}
        if self.action == "list":
            context["only"] = {
                "id",
                "type",
                "name",
                "status",
                "is_open",
                "is_suspended",
                "created_at",
                "closed_at",
                "days_open",
                "url",
                "issue__id",
                "issue__fileref",
                "issue__topic",
                "issue__url",
                "owner__id",
                "owner__full_name",
                "owner__url",
                "assigned_to__id",
                "assigned_to__full_name",
                "assigned_to__url",
            }
        return context

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
        queryset = queryset.select_related("issue", "owner", "assigned_to")

        if self.action == "retrieve":
            queryset = queryset.prefetch_related("comments", "attachments")
        elif self.action == "list":
            queryset = queryset.order_by("-days_open")
            queryset = self.search_queryset(queryset)

        # Permissions.
        if user.is_paralegal:
            queryset = queryset.filter(Q(owner=user) | Q(assigned_to=user))
            # Double check: Even if they are the owner or assigned to a task
            # paralegals should only be able to see the tasks related to cases
            # of which they are the assigned paralegal.
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
                            | Q(owner__first_name__icontains=part)
                            | Q(owner__last_name__icontains=part)
                            | Q(owner__email__icontains=part)
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
                        query = Q(owner=self.request.user) | Q(
                            assigned_to=self.request.user
                        )
                        queryset = queryset.filter(query)
                else:
                    queryset = queryset.filter(**{key: value})

        return queryset
