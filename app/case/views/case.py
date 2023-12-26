from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, action
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q, Max, QuerySet
from django.shortcuts import get_object_or_404
from django.urls import reverse


from core.models import Issue, IssueNote
from core.models.issue import CaseStage, CaseOutcome, CaseTopic
from case.utils import render_react_page, ClerkPaginator
from case.serializers import (
    IssueSerializer,
    IssueSearchSerializer,
    IssueNoteSerializer,
    TenancySerializer,
)
from case.views.auth import (
    paralegal_or_better_required,
    coordinator_or_better_required,
    ParalegalOrBetterObjectPermission,
    CoordinatorOrBetterPermission,
)
from microsoft.service import get_case_folder_info


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


@api_view(["GET"])
@coordinator_or_better_required
def case_inbox_page_view(request):
    """Inbox page where coordinators can see new cases for them to assign"""
    is_unassigned = Q(paralegal__isnull=True)
    is_open = Q(is_open=True)
    is_inbox = is_unassigned & is_open
    issues = (
        Issue.objects.select_related("client")
        .prefetch_related("issuenote_set", "paralegal__groups", "lawyer__groups")
        .filter(is_inbox)
        .order_by("created_at")
    )
    issues = IssueNote.annotate_with_eligibility_checks(issues)
    context = {"issues": IssueSerializer(issues, many=True).data}
    return render_react_page(request, "Case Inbox", "case-inbox", context)


@api_view(["GET"])
@coordinator_or_better_required
def case_review_page_view(request):
    """Page where coordinators can see existing cases for them to review"""
    issues = (
        Issue.objects.select_related("client")
        .prefetch_related("issuenote_set", "paralegal__groups", "lawyer__groups")
        .filter(is_open=True)
        .annotate(next_review=Max("issuenote__event"))
        .order_by("next_review")
    )
    issues = IssueNote.annotate_with_eligibility_checks(issues)
    context = {"issues": IssueSerializer(issues, many=True).data}
    return render_react_page(request, "Case Review", "case-review", context)


@api_view(["GET"])
@paralegal_or_better_required
def case_detail_page_view(request, pk):
    """
    The details of a given case.
    """
    issue = get_object_or_404(Issue, pk=pk)
    context = {"case_pk": pk, "urls": get_detail_urls(issue)}
    return render_react_page(request, f"Case {issue.fileref}", "case-detail", context)


@api_view(["GET"])
@paralegal_or_better_required
def case_detail_documents_page_view(request, pk):
    """
    The documents of a given case.
    """
    issue = get_object_or_404(Issue, pk=pk)
    context = {"case_pk": pk, "urls": get_detail_urls(issue)}
    return render_react_page(request, f"Case {issue.fileref}", "document-list", context)


def get_detail_urls(issue: Issue):
    return {
        "detail": reverse("case-detail", args=(issue.pk,)),
        "email": reverse("case-email-list", args=(issue.pk,)),
        "docs": reverse("case-docs", args=(issue.pk,)),
    }


class CasePaginator(ClerkPaginator):
    page_size = 14
    max_page_size = 14


class CaseApiViewset(GenericViewSet, ListModelMixin, UpdateModelMixin):
    serializer_class = IssueSerializer
    pagination_class = CasePaginator

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

        if self.action == "list":
            queryset = self.search_queryset(queryset)

        return queryset

    def search_queryset(self, queryset: QuerySet[Issue]) -> QuerySet[Issue]:
        """
        Filter queryset by search terms in query params
        """
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

    def retrieve(self, request, *args, **kwargs):
        """
        Get a single issue
        """
        # Get issue data
        issue = self.get_object()
        issue_serializer = self.get_serializer(issue)
        issue_data = issue_serializer.data

        # Get issue notes
        user = self.request.user
        if user.is_coordinator_or_better:
            note_types = IssueNote.COORDINATOR_NOTE_TYPES
        else:
            note_types = IssueNote.PARALEGAL_NOTE_TYPES

        notes = (
            IssueNote.objects.filter(issue=issue.pk)
            .prefetch_related("creator__groups")
            .filter(note_type__in=note_types)
            .order_by("-created_at")
            .all()
        )
        note_data = IssueNoteSerializer(notes, many=True).data

        # Get tenancy data
        tenancy = issue.client.tenancy_set.first()
        tenancy_data = TenancySerializer(tenancy).data

        # Return composite response
        response_data = {
            "issue": issue_data,
            "tenancy": tenancy_data,
            "notes": note_data,
        }
        return Response(response_data)

    @action(
        detail=True,
        methods=["POST"],
        url_path="note",
        url_name="note",
    )
    def create_note_view(self, request, pk):
        """
        Add a note to an existing issue.
        """
        issue = self.get_object()  # Checks permissions
        data = {
            **request.data,
            "issue": issue.pk,
            "creator_id": self.request.user.pk,
        }
        serializer = IssueNoteSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)

    @action(
        detail=True,
        methods=["GET"],
        url_path="docs",
        url_name="docs",
    )
    def get_documents_view(self, request, pk):
        """
        View sharepoint documents for a case.
        """
        issue = self.get_object()
        documents, sharepoint_url = get_case_folder_info(issue)
        data = {"sharepoint_url": sharepoint_url, "documents": documents}
        return Response(data)
