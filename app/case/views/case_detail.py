from django.http import Http404, HttpResponseBadRequest
from django.urls import reverse
from rest_framework.decorators import api_view
from rest_framework.response import Response


from case.views.auth import paralegal_or_better_required, coordinator_or_better_required
from core.models import Issue, IssueNote, Person
from case.utils.react import render_react_page
from case.serializers import (
    IssueSerializer,
    TenancySerializer,
    IssueNoteSerializer,
    IssueAssignmentSerializer,
    PersonSerializer,
)


# @api_view(["GET"])
# @paralegal_or_better_required
# def case_detail_view(request, pk):
#     """
#     The details of a given case.
#     """
#     issue = _get_issue(request, pk)
#     tenancy = _get_tenancy(issue)
#     notes = _get_issue_notes(request, pk)
#     context = {
#         "issue": IssueSerializer(issue).data,
#         "tenancy": TenancySerializer(tenancy).data,
#         "notes": IssueNoteSerializer(notes, many=True).data,
#         "details": _get_submitted_details(issue),
#         "actionstep_url": _get_actionstep_url(issue),
#         "urls": get_detail_urls(issue),
#         "permissions": {
#             "is_paralegal_or_better": request.user.is_paralegal_or_better,
#             "is_coordinator_or_better": request.user.is_coordinator_or_better,
#         },
#     }
#     return render_react_page(request, f"Case {issue.fileref}", "case-detail", context)


def get_detail_urls(issue):
    return {
        "detail": reverse("case-detail", args=(issue.pk,)),
        "email": reverse("case-email-list", args=(issue.pk,)),
        "docs": reverse("case-docs", args=(issue.pk,)),
    }


# @api_view(["POST", "DELETE"])
# @paralegal_or_better_required
# def agent_select_view(request, pk):
#     """
#     User can add or remove an agent for a given case.
#     """
#     return _person_select_view(request, pk, "agent")


# @api_view(["POST", "DELETE"])
# @paralegal_or_better_required
# def landlord_select_view(request, pk):
#     """
#     User can add or remove a landlord for a given case.
#     """
#     return _person_select_view(request, pk, "landlord")


# def _person_select_view(request, pk, person_type):
#     issue = _get_issue(request, pk)
#     tenancy = _get_tenancy(issue)
#     if request.method == "DELETE":
#         # User is deleting the person from the tenancy.
#         setattr(tenancy, person_type, None)
#         tenancy.save()
#     elif request.method == "POST":
#         # User is adding a person from the tenancy.
#         person_pk = request.data.get("person_id")
#         if person_pk is None:
#             return HttpResponseBadRequest()

#         person = Person.objects.get(pk=int(person_pk))
#         setattr(tenancy, person_type, person)
#         tenancy.save()

#     return Response(TenancySerializer(tenancy).data)


# @api_view(["POST", "DELETE"])
# @paralegal_or_better_required
# def support_worker_select_view(request, pk):
#     """
#     User can add or remove a support worker for a given case.
#     """
#     issue = _get_issue(request, pk)
#     if request.method == "DELETE":
#         # User is deleting the person from the tenancy.
#         issue.support_worker = None
#         issue.save()
#         return Response(status=200)
#     elif request.method == "POST":
#         # User is adding a person from the tenancy.
#         person_pk = request.data.get("person_id")
#         if person_pk is None:
#             return HttpResponseBadRequest()

#         person = Person.objects.get(pk=int(person_pk))
#         issue.support_worker = person
#         issue.save()
#         return Response(PersonSerializer(person).data)


@api_view(["POST"])
@paralegal_or_better_required
def case_detail_note_view(request, pk):
    """
    Form where paralegals can leave notes about case progress.
    """
    issue = _get_issue(request, pk)
    data = {
        "issue": issue.id,
        "creator": request.user.id,
        **request.data,
    }
    serializer = IssueNoteCreateSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    notes = _get_issue_notes(request, pk)
    return Response(
        {
            "issue": IssueSerializer(issue).data,
            "notes": IssueNoteSerializer(notes, many=True).data,
        }
    )


@api_view(["POST"])
@paralegal_or_better_required
def case_detail_update_view(request, pk):
    """
    Form where you update the case status.
    """
    issue = _get_issue(request, pk)
    serializer = IssueSerializer(data=request.data, instance=issue, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response({"issue": IssueSerializer(issue).data})


@api_view(["POST"])
@coordinator_or_better_required
def case_detail_assign_view(request, pk):
    """
    Form where coordinators can assign a paralegal to a case
    """
    issue = _get_issue(request, pk)
    serializer = IssueAssignmentSerializer(data=request.data, instance=issue)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response({"issue": IssueSerializer(issue).data})


# def _get_tenancy(issue):
#     # FIXME: Assume only only tenancy but that's not how the models work.
#     tenancy = issue.client.tenancy_set.first()
#     return tenancy


def _get_issue(request, pk):
    try:
        issue = (
            Issue.objects.check_permissions(request)
            .select_related("client", "paralegal", "lawyer")
            .prefetch_related("fileupload_set")
            .get(pk=pk)
        )
    except Issue.DoesNotExist:
        raise Http404()

    return issue


# def _get_submitted_details(issue):
#     details = {}
#     correct_case = lambda s: s.lower().capitalize()
#     for name, answer in issue.answers.items():
#         if answer is None:
#             continue
#         title = correct_case(" ".join(name.split("_")[1:]))
#         answer = (
#             ", ".join([str(s) for s in answer]) if type(answer) is list else str(answer)
#         )
#         if "_" in answer:
#             answer = correct_case(" ".join(answer.split("_")))

#         details[title] = answer

#     return details


# def _get_issue_notes(request, pk):
#     """
#     Returns the issue notes visible to a given user.
#     """
#     if request.user.is_coordinator_or_better:
#         note_types = IssueNote.COORDINATOR_NOTE_TYPES
#     else:
#         note_types = IssueNote.PARALEGAL_NOTE_TYPES

#     return (
#         IssueNote.objects.filter(issue=pk)
#         .prefetch_related("creator__groups")
#         .filter(note_type__in=note_types)
#         .order_by("-created_at")
#         .all()
#     )


# def _get_actionstep_url(issue):
#     if issue.actionstep_id:
#         return f"https://ap-southeast-2.actionstep.com/mym/asfw/workflow/action/overview/action_id/{issue.actionstep_id}"
