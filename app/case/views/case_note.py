import logging

from django.db.models import QuerySet, Q
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin

from core.models import IssueNote
from case.views.auth import (
    ParalegalOrBetterObjectPermission,
    CoordinatorOrBetterPermission,
)
from case.serializers import (
    IssueNoteSerializer,
    IssueNoteSearchSerializer,
)
from case.utils import ClerkPaginator

logger = logging.getLogger(__name__)


class CaseNotePaginator(ClerkPaginator):
    page_size = 20
    max_page_size = 100


class CaseNoteApiViewset(GenericViewSet, ListModelMixin, RetrieveModelMixin):
    serializer_class = IssueNoteSerializer
    pagination_class = CaseNotePaginator

    def get_permissions(self):
        if self.action == "list":
            permission_classes = [ParalegalOrBetterObjectPermission]
        else:
            permission_classes = [CoordinatorOrBetterPermission]

        return [p() for p in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if user.is_coordinator_or_better:
            note_types = IssueNote.COORDINATOR_NOTE_TYPES
        else:
            note_types = IssueNote.PARALEGAL_NOTE_TYPES

        queryset = (
            IssueNote.objects.prefetch_related("creator__groups")
            .filter(note_type__in=note_types)
            .order_by("-created_at")
        )

        if self.action == "list":
            queryset = self.search_queryset(queryset)

            if user.is_paralegal:
                # Paralegals can only view their own & so-called system
                # accounts.
                query = Q(creator=user)
                query |= Q(issue__paralegal=user)
                queryset = queryset.filter(query)

        return queryset

    def search_queryset(self, queryset: QuerySet[IssueNote]) -> QuerySet[IssueNote]:
        """
        Filter queryset by search terms in query params
        """
        search_query_serializer = IssueNoteSearchSerializer(
            data=self.request.query_params, partial=True
        )
        search_query_serializer.is_valid(raise_exception=True)
        search_query = search_query_serializer.validated_data

        for key, value in search_query.items():
            if value is not None:
                queryset = queryset.filter(**{key: value})

        return queryset
