import logging

from django.db.models import QuerySet, Q
from django.contrib.contenttypes.models import ContentType
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin

from accounts.models import User
from core.models import IssueNote
from core.models.issue_note import NoteType
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


class NotePaginator(ClerkPaginator):
    page_size = 20
    max_page_size = 100


class NoteApiViewset(GenericViewSet, ListModelMixin, RetrieveModelMixin):
    serializer_class = IssueNoteSerializer
    pagination_class = NotePaginator

    def get_permissions(self):
        if self.action == "list":
            permission_classes = [ParalegalOrBetterObjectPermission]
        else:
            permission_classes = [CoordinatorOrBetterPermission]

        return [p() for p in permission_classes]

    def get_queryset(self):
        user = self.request.user

        # Paralegals are restricted in the type of notes they can access.
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

           # Paralegals & lawyers can only view their own notes & the notes added to
           # issues to which they are assigned.
            if user.is_paralegal:
                queryset = queryset.filter(Q(creator=user) | Q(issue__paralegal=user))
            elif user.is_lawyer:
                queryset = queryset.filter(Q(creator=user) | Q(issue__lawyer=user))

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
            if value != None:
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
