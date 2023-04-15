from django.http import Http404
from django.db.models import Q
from django.urls import reverse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from core.models import Person, Issue
from case.utils.router import Router
from case.utils.react import render_react_page, is_react_api_call
from case.serializers import PersonSerializer, IssueDetailSerializer
from .auth import paralegal_or_better_required


router = Router("person")
router.create_route("detail").pk("pk")
router.create_route("create").path("create")
router.create_route("search").path("search")
router.create_route("list")


@router.use_route("create")
@paralegal_or_better_required
@api_view(["GET", "POST"])
def person_create_view(request):
    if request.method == "POST":
        serializer = PersonSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return render_react_page(request, "Create person", "person-create", {})


@router.use_route("search")
@paralegal_or_better_required
@api_view(["GET"])
def person_search_view(request):
    people_qs = Person.objects.order_by("full_name").all()
    query = request.GET.get("person")
    if query:
        q_filter = (
            Q(full_name__icontains=query)
            | Q(email__icontains=query)
            | Q(address__icontains=query)
            | Q(phone_number__icontains=query)
        )
        people_qs = people_qs.filter(q_filter)

    return Response(data=PersonSerializer(people_qs, many=True).data)


@router.use_route("list")
@paralegal_or_better_required
@api_view(["GET"])
def person_list_view(request):
    people_qs = Person.objects.order_by("full_name").all()
    people = PersonSerializer(people_qs, many=True).data
    if is_react_api_call(request):
        return Response(data=people)
    else:
        context = {
            "people": people,
            "create_url": reverse("person-create"),
        }
        return render_react_page(request, "People", "person-list", context)


@router.use_route("detail")
@paralegal_or_better_required
@api_view(["GET", "PUT", "DELETE"])
def person_detail_view(request, pk):
    try:
        person = Person.objects.get(pk=pk)
    except Person.DoesNotExist:
        raise Http404()

    if request.method == "DELETE":
        if request.user.is_coordinator_or_better:
            person.delete()
            return Response({})
        else:
            raise Http404()

    if request.method == "PUT":
        if request.user.is_coordinator_or_better:
            serializer = PersonSerializer(instance=person, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            raise Http404()

    q_filter = Q(client__tenancy__agent=person) | Q(client__tenancy__landlord=person)
    issues = Issue.objects.filter(q_filter).order_by("-created_at").all()

    context = {
        "issues": IssueDetailSerializer(issues, many=True).data,
        "person": PersonSerializer(instance=person).data,
        "is_editable": request.user.is_coordinator_or_better,
        "list_url": reverse("person-list"),
    }
    return render_react_page(request, person.full_name, "person-detail", context)
