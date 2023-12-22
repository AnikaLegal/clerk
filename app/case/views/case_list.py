from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.db.models import Q

from core.models import Issue
from core.models.issue import CaseStage, CaseOutcome, CaseTopic
from case.utils.react import render_react_page
from case.serializers import IssueSerializer, IssueSearchSerializer


COORDINATORS_EMAIL = "coordinators@anikalegal.com"


@login_required
@api_view(["GET"])
def case_list_page_view(request):
    """
    List of all cases for paralegals and coordinators to view.
    """
    context = {
        "choices": {
            "stage": CaseStage.CHOICES,
            "topic": CaseTopic.CHOICES,
            "outcome": CaseOutcome.CHOICES,
            "is_open": [
                ("True", "Open"),
                ("False", "Closed"),
            ],
        },
    }
    return render_react_page(request, f"Cases", "case-list", context)


class CasePaginator(PageNumberPagination):
    page_size = 14
    max_page_size = 14

    def get_paginated_response(self, data):
        next_page_number, prev_page_number = None, None
        if self.page.has_next():
            next_page_number = self.page.next_page_number()

        if self.page.has_previous():
            prev_page_number = self.page.previous_page_number()

        return Response(
            {
                "page_count": self.page.paginator.num_pages,
                "item_count": self.page.paginator.count,
                "current": self.page.number,
                "next": next_page_number,
                "prev": prev_page_number,
                "results": data,
            }
        )


class CaseApiViewset(GenericViewSet, ListModelMixin):
    serializer_class = IssueSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CasePaginator

    def get_queryset(self):
        """Filter by query params"""
        user = self.request.user
        queryset = (
            Issue.objects.select_related("client")
            .prefetch_related("paralegal__groups", "lawyer__groups")
            .order_by("-created_at")
        )
        if user.is_paralegal:
            # Paralegals can only see assigned cases
            queryset = queryset.filter(paralegal=user)
        elif not user.is_coordinator_or_better:
            # If you're not a paralegal or coordinator you can't see nuthin.
            queryset = queryset.none()

        search_query_serializer = IssueSearchSerializer(
            data=self.request.query_params, partial=True
        )
        search_query_serializer.is_valid(raise_exception=True)
        search_query = search_query_serializer.validated_data
        for key, value in search_query.items():
            if key == "search" and value:
                # Run free text search query
                search_parts = value.split(" ")
                search_query = None
                for search_part in search_parts:
                    part_query = (
                        Q(paralegal__first_name__icontains=search_part)
                        | Q(paralegal__last_name__icontains=search_part)
                        | Q(paralegal__email__icontains=search_part)
                        | Q(client__first_name__icontains=search_part)
                        | Q(client__last_name__icontains=search_part)
                        | Q(client__email__icontains=search_part)
                        | Q(fileref__icontains=search_part)
                    )
                    if search_query:
                        search_query |= part_query
                    else:
                        search_query = part_query

                queryset = queryset.filter(search_query)
            else:
                # Apply basic field filtering
                queryset = queryset.filter(**{key: value})

        return queryset
