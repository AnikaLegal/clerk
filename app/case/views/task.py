from django.db.models import Q
from django.db.models import Q, QuerySet
from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import api_view

from case.views.auth import (
    paralegal_or_better_required,
    CoordinatorOrBetterPermission,
    ParalegalOrBetterObjectPermission,
)
from case.utils.react import render_react_page
from task.models import Task
from task.serializers import TaskSerializer, TaskSearchSerializer

# TODO:
# - review permissions.


@api_view(["GET"])
@paralegal_or_better_required
def task_list_page_view(request):
    context = {}
    return render_react_page(request, "Tasks", "task-list", context)


@api_view(["GET"])
@paralegal_or_better_required
def task_detail_page_view(request, pk):
    context = {"task_pk": pk}
    return render_react_page(request, "Task", "task-detail", context)


class TaskApiViewset(ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [
        CoordinatorOrBetterPermission | ParalegalOrBetterObjectPermission
    ]

    def get_queryset(self):
        user = self.request.user
        queryset = Task.objects.filter(Q(owner=user) | Q(assigned_to=user))
        queryset = queryset.select_related("issue", "owner", "assigned_to")

        if self.action == "retrieve":
            queryset = queryset.prefetch_related("comments", "attachments")
        elif self.action == "list":
            queryset = self.search_queryset(queryset)

        # Permissions.
        if user.is_paralegal:
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
            queryset = queryset.filter(**{key: value})

        return queryset
