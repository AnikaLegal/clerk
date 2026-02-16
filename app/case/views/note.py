from accounts.models import User
from core.models import IssueNote
from core.models.issue_note import NoteType
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, QuerySet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from case.serializers import (
    IssueNoteSearchSerializer,
    IssueNoteSerializer,
)
from case.utils import ClerkPaginator
from case.views.auth import (
    CoordinatorOrBetterPermission,
    ParalegalOrBetterObjectPermission,
)


class NotePaginator(ClerkPaginator):
    page_size = 20
    max_page_size = 100


class NoteApiViewset(GenericViewSet, ListModelMixin, RetrieveModelMixin):
    serializer_class = IssueNoteSerializer
    pagination_class = NotePaginator
    permission_classes = [
        CoordinatorOrBetterPermission,
        ParalegalOrBetterObjectPermission,
    ]

    def get_queryset(self):
        user = self.request.user

        # Paralegals are restricted in the type of notes they can access.
        if user.is_coordinator_or_better:
            note_types = IssueNote.COORDINATOR_NOTE_TYPES
        else:
            note_types = IssueNote.PARALEGAL_NOTE_TYPES

        queryset = (
            IssueNote.objects.select_related("issue__paralegal", "issue__lawyer")
            .prefetch_related("creator__groups")
            .filter(note_type__in=note_types)
            .order_by("-created_at")
        )

        if self.action == "list":
            queryset = self.list_queryset(queryset)

        return queryset

    def list_queryset(self, queryset: QuerySet[IssueNote]) -> QuerySet[IssueNote]:
        user = self.request.user
        queryset = self.search_queryset(queryset)

        # Paralegals & lawyers can only view their own notes & the notes added to
        # issues to which they are assigned.
        if not user.is_coordinator_or_better:
            queryset = queryset.filter(
                Q(creator=user) | Q(issue__paralegal=user) | Q(issue__lawyer=user)
            )
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
            if key == "reviewee":
                user_type = ContentType.objects.get_for_model(User)
                queryset = queryset.filter(
                    note_type=NoteType.PERFORMANCE,
                    content_type=user_type,
                    object_id=value,
                )
            else:
                queryset = queryset.filter(**{key: value})

        return queryset
