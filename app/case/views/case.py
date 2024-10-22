from core.models import Issue, IssueNote
from core.models.issue import CaseOutcome, CaseStage, CaseTopic
from core.models.service import DiscreteServiceType, OngoingServiceType, ServiceCategory
from core.events.service import (
    on_service_create,
    on_service_delete,
    on_service_update,
)
from django.db.models import Max, Q, QuerySet
from django.shortcuts import get_object_or_404
from django.urls import reverse
from microsoft.service import get_case_folder_info
from rest_framework import status
from rest_framework.decorators import action, api_view
from rest_framework.mixins import ListModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from case.serializers import (
    IssueNoteSerializer,
    IssueSearchSerializer,
    IssueSerializer,
    ServiceSearchSerializer,
    ServiceSerializer,
    TenancySerializer,
)
from case.utils import ClerkPaginator, render_react_page
from case.views.auth import (
    CoordinatorOrBetterPermission,
    ParalegalOrBetterObjectPermission,
    coordinator_or_better_required,
    login_required,
    paralegal_or_better_required,
)

COORDINATORS_EMAIL = "coordinators@anikalegal.com"


@api_view(["GET"])
@login_required
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
    return render_react_page(request, "Cases", "case-list", context)


@api_view(["GET"])
@coordinator_or_better_required
def case_inbox_page_view(request):
    """Inbox page where coordinators can see new cases for them to assign"""
    is_unassigned = Q(paralegal__isnull=True)
    is_open = Q(is_open=True)
    is_inbox = is_unassigned & is_open
    issues = (
        Issue.objects.select_related("client", "tenancy__agent", "tenancy__landlord")
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
        Issue.objects.select_related("client", "tenancy__agent", "tenancy__landlord")
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
    context = {
        "case_pk": pk,
        "choices": {
            "service": {
                "category": ServiceCategory.choices,
                "type_DISCRETE": DiscreteServiceType.choices,
                "type_ONGOING": OngoingServiceType.choices,
            },
        },
        "urls": get_detail_urls(issue),
    }
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


@api_view(["GET"])
@paralegal_or_better_required
def case_detail_services_page_view(request, pk):
    """
    The services related to a case.
    """
    issue = get_object_or_404(Issue, pk=pk)
    context = {
        "case_pk": pk,
        "urls": get_detail_urls(issue),
        "choices": {
            "category": ServiceCategory.choices,
            "type_DISCRETE": DiscreteServiceType.choices,
            "type_ONGOING": OngoingServiceType.choices,
        },
    }
    return render_react_page(request, f"Case {issue.fileref}", "service-list", context)


def get_detail_urls(issue: Issue):
    return {
        "detail": reverse("case-detail", args=(issue.pk,)),
        "email": reverse("case-email-list", args=(issue.pk,)),
        "docs": reverse("case-docs", args=(issue.pk,)),
        "services": reverse("case-services", args=(issue.pk,)),
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
            Issue.objects.select_related(
                "client", "tenancy__agent", "tenancy__landlord"
            )
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
        tenancy_data = TenancySerializer(issue.tenancy).data

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
            "issue_id": issue.pk,
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

    @action(
        detail=True,
        methods=["GET", "POST"],
        url_path="services",
        url_name="service-list",
        serializer_class=ServiceSerializer,
    )
    def service_list(self, request, pk):
        """
        List or create case services.
        """
        issue = self.get_object()

        if request.method == "GET":
            queryset = issue.service_set.all()
            queryset = queryset.order_by("-started_at")

            serializer = ServiceSearchSerializer(
                data=self.request.query_params, partial=True
            )
            serializer.is_valid(raise_exception=True)
            terms = serializer.validated_data
            for key, value in terms.items():
                if value is not None:
                    queryset = queryset.filter(**{key: value})

            data = self.get_serializer(queryset, many=True).data
            return Response(data)
        else:
            data = {**request.data, "issue_id": issue.pk}
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            on_service_create(service=dict(serializer.data), user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=["GET", "PATCH", "DELETE"],
        url_path="services/(?P<service_pk>[^/.]+)",
        url_name="service-detail",
        serializer_class=ServiceSerializer,
    )
    def service_detail(self, request, pk, service_pk):
        """
        Get, update or delete a particular case service.
        """
        issue = self.get_object()
        service = get_object_or_404(issue.service_set, pk=service_pk)

        if request.method == "DELETE":
            data = self.get_serializer(service).data
            service.delete()
            on_service_delete(service=dict(data), user=request.user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        elif request.method == "PATCH":
            serializer = self.get_serializer(service, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            on_service_update(service=dict(serializer.data), user=request.user)
            return Response(serializer.data)
        else:
            serializer = self.get_serializer(service)
            return Response(serializer.data)
