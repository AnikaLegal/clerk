from core.models import Issue, IssueDate
from django.db.models import QuerySet, Q
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
    return render_react_page(request, "Critical Dates", "date-list", {})


class DatePaginator(ClerkPaginator):
    page_size = 20


class DateApiViewSet(viewsets.ModelViewSet):
    """
    API endpoint for case dates.
    """

    queryset = IssueDate.objects.all()
    serializer_class = IssueDateSerializer
    pagination_class = DatePaginator
    permission_classes = [
        CoordinatorOrBetterPermission | ParalegalOrBetterObjectPermission
    ]

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related(
            "issue",
            "issue__client",
            "issue__tenancy__landlord",
            "issue__tenancy__agent",
            "issue__paralegal",
            "issue__lawyer",
            "issue__support_worker",
        )
        queryset = queryset.prefetch_related(
            "issue__paralegal__groups", "issue__lawyer__groups"
        )

        if self.action == "list":
            queryset = self.list_queryset(queryset)
            queryset = self.search_queryset(queryset)
            queryset = queryset.order_by("date", "type", "created_at")

        return queryset

    def list_queryset(self, queryset: QuerySet[IssueDate]) -> QuerySet[IssueDate]:
        user = self.request.user
        if user.is_paralegal:
            # Paralegals can only see the dates for cases to which they are assigned.
            queryset = queryset.filter(issue__paralegal=user)
        elif not user.is_coordinator_or_better:
            # If you're not a paralegal or coordinator you can't see anything.
            queryset = queryset.none()
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
                if key == "q":
                    # Search by fileref or client details
                    queryset = queryset.filter(
                        Q(issue__fileref__icontains=value)
                        | Q(issue__client__first_name__icontains=value)
                        | Q(issue__client__last_name__icontains=value)
                        | Q(issue__client__email__icontains=value)
                    )
                else:
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
