from core.models import Issue, IssueDate
from core.models.issue_date import DateType
from django.db.models import QuerySet
from rest_framework import viewsets
from rest_framework.decorators import api_view

from case.serializers.issue_date import IssueDateSearchSerializer, IssueDateSerializer
from case.utils import ClerkPaginator, render_react_page
from case.views.auth import (
    CoordinatorOrBetterPermission,
    ParalegalOrBetterObjectPermission,
    coordinator_or_better_required,
)


@api_view(["GET"])
@coordinator_or_better_required
def date_list_page_view(request):
    context = {
        "choices": {
            "type": DateType.choices,
        }
    }
    return render_react_page(request, "Critical Dates", "date-list", context)


class DatePaginator(ClerkPaginator):
    page_size = 20


class DateApiViewSet(viewsets.ModelViewSet):
    """
    API endpoint for viewing, creating, updating, and deleting IssueDate objects.
    """

    serializer_class = IssueDateSerializer
    pagination_class = DatePaginator
    permission_classes = [
        CoordinatorOrBetterPermission | ParalegalOrBetterObjectPermission
    ]

    def get_queryset(self):
        user = self.request.user
        queryset = IssueDate.objects.all()
        queryset = queryset.select_related(
            "creator",
            "issue",
            "issue__client",
            "issue__tenancy__landlord",
            "issue__tenancy__agent",
            "issue__paralegal",
            "issue__lawyer",
            "issue__support_worker",
        )
        queryset = queryset.prefetch_related(
            "creator__groups", "issue__paralegal__groups", "issue__lawyer__groups"
        )

        if user.is_paralegal:
            # Paralegals can only see the dates for cases to which they are assigned.
            queryset = queryset.filter(issue__paralegal=user)
        elif not user.is_coordinator_or_better:
            # If you're not a paralegal or coordinator you can't see anything.
            queryset = queryset.none()

        if self.action == "list":
            queryset = queryset.order_by("date")
            queryset = self.search_queryset(queryset)

        return queryset

    def search_queryset(self, queryset: QuerySet[IssueDate]) -> QuerySet[IssueDate]:
        """
        Filter queryset by search terms in query params
        """
        serializer = IssueDateSearchSerializer(
            data=self.request.query_params, partial=True
        )
        serializer.is_valid(raise_exception=True)
        assert isinstance(serializer.validated_data, dict)  # Keep type checker happy

        search_query = serializer.validated_data
        for key, value in search_query.items():
            if value is not None:
                queryset = queryset.filter(**{key: value})

        return queryset

    def create(self, request, *args, **kwargs):
        issue_id = request.data.get("issue_id")
        if issue_id:
            # Check the user has access to the issue before creating the date.
            try:
                issue = Issue.objects.get(id=issue_id)
                self.check_object_permissions(request, issue)
            except Issue.DoesNotExist:
                pass  # Handled by serializer validation

        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        return serializer.save(creator_id=self.request.user.pk)
