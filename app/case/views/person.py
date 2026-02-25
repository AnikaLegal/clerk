from core.models import Issue, Person
from django.db.models import Q, QuerySet
from django.http import Http404
from django.urls import reverse
from rest_framework.decorators import api_view
from rest_framework.viewsets import ModelViewSet

from case.serializers import (
    IssueSerializer,
    PersonSearchRequestSerializer,
    PersonSerializer,
)
from case.utils.pagination import ClerkPaginator
from case.utils.react import render_react_page

from .auth import (
    CoordinatorOrBetterCanWritePermission,
    coordinator_or_better_required,
    paralegal_or_better_required,
)


@api_view(["GET"])
@paralegal_or_better_required
def person_list_page_view(request):
    context = {"create_url": reverse("person-create")}
    return render_react_page(request, "People", "person-list", context)


@api_view(["GET"])
@coordinator_or_better_required
def person_create_page_view(request):
    return render_react_page(request, "Create person", "person-create", {})


@api_view(["GET"])
@paralegal_or_better_required
def person_detail_page_view(request, pk):
    try:
        person = Person.objects.get(pk=pk)
    except Person.DoesNotExist:
        raise Http404()

    q_filter = Q(tenancy__agent=person) | Q(tenancy__landlord=person)
    issues = Issue.objects.filter(q_filter).order_by("-created_at").all()

    context = {
        "issues": IssueSerializer(issues, many=True).data,
        "person": PersonSerializer(instance=person).data,
        "is_editable": request.user.is_coordinator_or_better,
        "list_url": reverse("person-list"),
    }
    return render_react_page(request, person.full_name, "person-detail", context)


class PersonPaginator(ClerkPaginator):
    page_size = 20


class PersonApiViewset(ModelViewSet):
    queryset = Person.objects.order_by("full_name").all()
    serializer_class = PersonSerializer
    pagination_class = PersonPaginator
    permission_classes = [CoordinatorOrBetterCanWritePermission]

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.action == "list":
            queryset = self.search_queryset(queryset)

        return queryset

    def search_queryset(self, queryset: QuerySet[Person]) -> QuerySet[Person]:
        serializer = PersonSearchRequestSerializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)

        query = serializer.validated_data.get("query")
        if query:
            q_filter = (
                Q(full_name__icontains=query)
                | Q(email__icontains=query)
                | Q(address__icontains=query)
                | Q(phone_number__icontains=query)
            )
            queryset = queryset.filter(q_filter)

        return queryset
