from django.db.models import Q
from django.db.models import Q, QuerySet
from rest_framework.viewsets import ModelViewSet

from case.views.auth import (
    CoordinatorOrBetterPermission,
    ParalegalOrBetterObjectPermission,
)
from task.models import Task
from task.serializers import TaskSerializer, TaskSearchSerializer

# TODO:
# - review permissions.


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
