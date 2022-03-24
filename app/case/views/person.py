from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.http import Http404
from django.db.models import Q
from rest_framework.decorators import api_view
from rest_framework.response import Response

from case.serializers import PersonSerializer
from case.utils.react import is_react_api_call
from case.forms import DynamicTableForm, PersonDynamicForm, PersonForm
from core.models import Person, Issue
from .auth import paralegal_or_better_required
from case.utils.router import Router


PERSON_DETAIL_FORMS = {
    "form": PersonDynamicForm,
}

router = Router("person")
router.create_route("detail").pk("pk").slug("form_slug", optional=True)
router.create_route("create").path("create")
router.create_route("search").path("search")
router.create_route("list")


@router.use_route("create")
@paralegal_or_better_required
@require_http_methods(["GET", "POST"])
def person_create_view(request):
    if request.method == "POST":
        form = PersonForm(request.POST)
        if form.is_valid():
            person = form.save()
            return redirect("person-detail", person.pk)
    else:
        form = PersonForm()

    context = {"form": form}
    return render(request, "case/person/create.html", context)


@router.use_route("search")
@paralegal_or_better_required
@require_http_methods(["GET"])
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

    context = {"people": people_qs}
    return render(request, "case/person/_list_table.html", context)


@router.use_route("list")
@paralegal_or_better_required
@api_view(["GET"])
def person_list_view(request):
    people = Person.objects.order_by("full_name").all()
    if is_react_api_call(request):
        return Response(data=PersonSerializer(people, many=True).data)
    else:
        context = {"people": people}
        return render(request, "case/person/list.html", context)


@router.use_route("detail")
@paralegal_or_better_required
@require_http_methods(["GET", "POST"])
def person_detail_view(request, pk, form_slug: str = ""):
    try:
        person = Person.objects.get(pk=pk)
    except Person.DoesNotExist:
        raise Http404()

    q_filter = Q(client__tenancy__agent=person) | Q(client__tenancy__landlord=person)
    issues = Issue.objects.filter(q_filter).order_by("-created_at").all()
    forms = DynamicTableForm.build_forms(
        request, form_slug, person, PERSON_DETAIL_FORMS
    )
    context = {"person": person, "forms": forms, "issues": issues}
    form_resp = DynamicTableForm.get_response(request, form_slug, forms, context)
    if form_resp:
        return form_resp
    else:
        return render(request, "case/person/detail.html", context)
