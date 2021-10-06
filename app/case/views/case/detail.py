from django.http import Http404, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from case.forms import (
    IssueProgressForm,
    ParalegalNoteForm,
    CaseReviewNoteForm,
    IssueAssignParalegalForm,
    IssueCloseForm,
    IssueOutcomeForm,
    IssueReOpenForm,
    ParalegalReviewNoteForm,
)
from case.utils import Selector, HtmxFormView
from core.models import Issue, IssueNote, Person
from core.models.issue_note import NoteType

from case.views.auth import paralegal_or_better_required
from case.utils.router import Route

MAYBE_IMAGE_FILE_EXTENSIONS = [".png", ".jpg", ".jpeg"]

detail_route = Route("detail").uuid("pk").slug("form_slug", optional=True)
landlord_route = (
    Route("landlord").uuid("pk").path("landlord").pk("person_pk", optional=True)
)
agent_route = Route("agent").uuid("pk").path("agent").pk("person_pk", optional=True)


@detail_route
@paralegal_or_better_required
@require_http_methods(["GET", "POST"])
def case_detail_view(request, pk, form_slug=""):
    """
    The details of a given case.
    """
    issue, tenancy = _get_issue_and_tenancy(request, pk)
    case_selector = CaseSelector(request, issue)

    file_urls, image_urls = _get_uploaded_files(issue)
    context = {
        "issue": issue,
        "tenancy": tenancy,
        "actionstep_url": _get_actionstep_url(issue),
        "notes": _get_issue_notes(request, pk),
        "case_selector": case_selector,
        "details": _get_submitted_details(issue),
        "file_urls": file_urls,
        "image_urls": image_urls,
        "people": Person.objects.order_by("full_name").all(),
    }
    form_view = case_selector.handle(form_slug, context, pk)
    if form_view:
        return form_view
    else:
        return render(request, "case/case/detail.html", context)


@agent_route
@paralegal_or_better_required
@require_http_methods(["GET", "POST", "DELETE"])
def agent_selet_view(request, pk):
    return _person_select_view(request, pk, "agent")


@landlord_route
@paralegal_or_better_required
@require_http_methods(["GET", "POST", "DELETE"])
def landlord_selet_view(request, pk):
    return _person_select_view(request, pk, "landlord")


def _person_select_view(request, pk, person_type):
    issue, tenancy = _get_issue_and_tenancy(request, pk)
    title = "Landlord" if person_type == "landlord" else "Real estate agent"
    context = {
        "title": title,
        "issue": issue,
        "person": None,
        "url_path": f"case-{person_type}",
        "people": Person.objects.order_by("full_name").all(),
    }
    if request.method == "DELETE":
        # User is deleting the person from the tenancy.
        setattr(tenancy, person_type, None)
        tenancy.save()
    elif request.method == "POST":
        # User is adding a person from the tenancy.
        person_pk = request.POST.get("person_id")
        if person_pk is None:
            return HttpResponseBadRequest()

        person = Person.objects.get(pk=int(person_pk))
        setattr(tenancy, person_type, person)
        tenancy.save()
        context["person"] = person

    return render(request, "case/case/_person_details.html", context)


class CaseReviewHtmxFormView(HtmxFormView):
    """
    Form where coordinators can leave a note for other coordinators
    """

    template = "case/case/forms/_review_note.html"
    success_message = "Note created"
    form_cls = CaseReviewNoteForm

    def is_user_allowed(self, request):
        return request.user.is_coordinator_or_better

    def get_success_context(self, request, context, pk, *args, **kwargs):
        return {"notes": _get_issue_notes(request, pk)}

    def get_default_form_data(self, request, context, *args, **kwargs):
        return {
            "issue": context["issue"],
            "creator": request.user,
            "note_type": NoteType.REVIEW,
        }


class ParalegalReviewHtmxFormView(HtmxFormView):
    """
    Form where coordinators can leave a note on paralegal performance.
    """

    template = "case/case/forms/_paralegal_review_note.html"
    success_message = "Note created"
    form_cls = ParalegalReviewNoteForm

    def is_user_allowed(self, request):
        return request.user.is_coordinator_or_better

    def get_success_context(self, request, context, pk, *args, **kwargs):
        return {"notes": _get_issue_notes(request, pk)}

    def get_default_form_data(self, request, context, *args, **kwargs):
        return {
            "issue": context["issue"],
            "creator": request.user,
            "note_type": NoteType.PERFORMANCE,
        }


class FileNoteHtmxFormView(HtmxFormView):
    """
    Form where anyone working on the case can leave a public file note
    """

    template = "case/case/forms/_paralegal_note.html"
    success_message = "Note created"
    form_cls = ParalegalNoteForm

    def is_user_allowed(self, request):
        return request.user.is_paralegal_or_better

    def get_success_context(self, request, context, pk, *args, **kwargs):
        return {"notes": _get_issue_notes(request, pk)}

    def get_default_form_data(self, request, context, *args, **kwargs):
        return {
            "issue": context["issue"],
            "creator": request.user,
            "note_type": NoteType.PARALEGAL,
        }


class AssignParalegalHtmxFormView(HtmxFormView):
    """
    Form where coordinators can assign a paralegal to a case
    """

    template = "case/case/forms/_assign_paralegal.html"
    success_message = "Assignment successful"
    form_cls = IssueAssignParalegalForm

    def is_user_allowed(self, request):
        return request.user.is_coordinator_or_better

    def get_success_context(self, request, context, pk, *args, **kwargs):
        return {"new_paralegal": context["issue"].paralegal}

    def get_form_instance(self, request, context, *args, **kwargs):
        return context["issue"]


class CaseProgressHtmxFormView(HtmxFormView):
    """
    Form where anyone can progress the case.
    """

    template = "case/case/forms/_progress.html"
    success_message = "Update successful"
    form_cls = IssueProgressForm

    def is_user_allowed(self, request):
        return request.user.is_paralegal_or_better

    def get_form_instance(self, request, context, *args, **kwargs):
        return context["issue"]


class CaseCloseHtmxFormView(HtmxFormView):
    """
    Form where you close the case.
    """

    template = "case/case/forms/_close.html"
    success_message = "Case closed!"
    form_cls = IssueCloseForm

    def is_user_allowed(self, request):
        return request.user.is_coordinator_or_better

    def get_form_instance(self, request, context, *args, **kwargs):
        return context["issue"]


class CaseOutcomeHtmxFormView(HtmxFormView):
    """
    Form where you update the outcome of the case.
    """

    template = "case/case/forms/_outcome.html"
    success_message = "Outcome updated"
    form_cls = IssueOutcomeForm

    def is_user_allowed(self, request):
        return request.user.is_coordinator_or_better

    def get_form_instance(self, request, context, *args, **kwargs):
        return context["issue"]


class CaseReOpenHtmxFormView(HtmxFormView):
    """
    Form where you open the case.
    """

    template = "case/case/forms/_reopen.html"
    success_message = "Case re-opened"
    form_cls = IssueReOpenForm

    def is_user_allowed(self, request):
        return request.user.is_coordinator_or_better

    def get_form_instance(self, request, context, *args, **kwargs):
        return context["issue"]


class CaseSelector(Selector):
    """
    A drop down where users can select the actions that they want to take for a case.
    """

    def __init__(self, request, issue):
        super().__init__(request)
        self.options = {**CaseSelector.options}
        if issue.is_open:
            del self.options["reopen"]
        else:
            del self.options["close"]

        when_allowed = lambda view, req: view.is_user_allowed(req)
        when_closed = lambda view, req: when_allowed(view, req) and not issue.is_open
        when_open = lambda view, req: when_allowed(view, req) and issue.is_open
        self.render_when = {
            k: when_allowed
            for k in ("note", "review", "progress", "assign", "performance")
        }
        self.render_when["close"] = when_open
        self.render_when["reopen"] = when_closed
        self.render_when["outcome"] = when_closed

    slug = "case"
    default_text = "I want to..."
    render_when = {}
    child_views = {
        "note": FileNoteHtmxFormView(),
        "review": CaseReviewHtmxFormView(),
        "assign": AssignParalegalHtmxFormView(),
        "progress": CaseProgressHtmxFormView(),
        "performance": ParalegalReviewHtmxFormView(),
        "close": CaseCloseHtmxFormView(),
        "reopen": CaseReOpenHtmxFormView(),
        "outcome": CaseOutcomeHtmxFormView(),
    }
    options = {
        "note": "Add a file note",
        "review": "Add a coordinator's case review note",
        "performance": "Add a paralegal performance review note",
        "assign": "Assign a paralegal to the case",
        "progress": "Progress case status",
        "outcome": "Edit case outcome",
        "close": "Close the case",
        "reopen": "Re-open the case",
    }


def _get_issue_and_tenancy(request, pk):
    try:
        issue = (
            Issue.objects.check_permisisons(request)
            .select_related("client")
            .prefetch_related("fileupload_set")
            .get(pk=pk)
        )
    except Issue.DoesNotExist:
        raise Http404()

    # FIXME: Assume only only tenancy but that's not how the models work.
    tenancy = issue.client.tenancy_set.first()
    return issue, tenancy


def _get_uploaded_files(issue):
    file_urls, image_urls = [], []
    for upload in issue.fileupload_set.all():
        is_maybe_image = any(
            [upload.file.name.endswith(ext) for ext in MAYBE_IMAGE_FILE_EXTENSIONS]
        )
        if is_maybe_image:
            image_urls.append(upload.file.url)
        else:
            file_urls.append(upload.file.url)

    return file_urls, image_urls


def _get_submitted_details(issue):
    details = []
    correct_case = lambda s: s.lower().capitalize()
    for name, answer in issue.answers.items():
        if answer is None:
            continue
        title = correct_case(" ".join(name.split("_")[1:]))
        answer = ", ".join(answer) if type(answer) is list else str(answer)
        if "_" in answer:
            answer = correct_case(" ".join(answer.split("_")))

        details.append({"title": title, "answer": answer})

    return details


def _get_issue_notes(request, pk):
    """
    Returns the issue notes visible to a given user.
    """
    if request.user.is_coordinator_or_better:
        note_types = IssueNote.COORDINATOR_NOTE_TYPES
    else:
        note_types = IssueNote.PARALEGAL_NOTE_TYPES

    return (
        IssueNote.objects.filter(issue=pk)
        .select_related("creator")
        .filter(note_type__in=note_types)
        .order_by("-created_at")
        .all()
    )


def _get_actionstep_url(issue):
    if issue.actionstep_id:
        return f"https://ap-southeast-2.actionstep.com/mym/asfw/workflow/action/overview/action_id/{issue.actionstep_id}"
