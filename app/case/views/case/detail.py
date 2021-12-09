from django.http import Http404, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.utils.datastructures import MultiValueDict
from django.contrib import messages
from django.urls import reverse

from case.forms import (
    IssueProgressForm,
    ParalegalNoteForm,
    CaseReviewNoteForm,
    IssueAssignParalegalForm,
    IssueCloseForm,
    IssueOutcomeForm,
    ConflictCheckNoteForm,
    IssueReOpenForm,
    ParalegalReviewNoteForm,
)
from case.utils.router import Router
from case.views.auth import paralegal_or_better_required, coordinator_or_better_required
from core.models import Issue, IssueNote, Person
from core.models.issue_note import NoteType


MAYBE_IMAGE_FILE_EXTENSIONS = [".png", ".jpg", ".jpeg"]

router = Router("detail")


router.create_route("view").uuid("pk")
router.create_route("options").uuid("pk").path("options")
router.create_route("note").uuid("pk").path("note")
router.create_route("review").uuid("pk").path("review")
router.create_route("performance").uuid("pk").path("performance")
router.create_route("conflict").uuid("pk").path("conflict")
router.create_route("assign").uuid("pk").path("assign")
router.create_route("progress").uuid("pk").path("progress")
router.create_route("close").uuid("pk").path("close")
router.create_route("reopen").uuid("pk").path("reopen")
router.create_route("outcome").uuid("pk").path("outcome")
router.create_route("landlord").uuid("pk").path("landlord").pk(
    "person_pk", optional=True
)
router.create_route("agent").uuid("pk").path("agent").pk("person_pk", optional=True)


CASE_DETAIL_OPTIONS = {
    "note": {
        "icon": "clipboard outline",
        "text": "Add a file note",
        "render_when": lambda req, issue: req.user.is_paralegal_or_better,
    },
    "review": {
        "icon": "clipboard outline",
        "text": "Add a coordinator case review note",
        "render_when": lambda req, issue: req.user.is_coordinator_or_better,
    },
    "performance": {
        "icon": "clipboard outline",
        "text": "Add a paralegal performance review note",
        "render_when": lambda req, issue: req.user.is_coordinator_or_better,
    },
    "conflict": {
        "icon": "search",
        "text": "Record a conflict check",
        "render_when": lambda req, issue: req.user.is_paralegal_or_better,
    },
    "assign": {
        "icon": "graduation cap",
        "text": "Assign a paralegal to the case",
        "render_when": lambda req, issue: req.user.is_coordinator_or_better,
    },
    "progress": {
        "icon": "chart line",
        "text": "Progress the case status",
        "render_when": lambda req, issue: req.user.is_paralegal_or_better,
    },
    "close": {
        "icon": "times circle outline",
        "text": "Close the case",
        "render_when": lambda req, issue: req.user.is_coordinator_or_better
        and issue.is_open,
    },
    "reopen": {
        "icon": "check",
        "text": "Re-open the case",
        "render_when": lambda req, issue: req.user.is_coordinator_or_better
        and not issue.is_open,
    },
    "outcome": {
        "icon": "undo",
        "text": "Edit case outcome",
        "render_when": lambda req, issue: req.user.is_coordinator_or_better
        and not issue.is_open,
    },
}


@router.use_route("view")
@paralegal_or_better_required
@require_http_methods(["GET", "POST"])
def case_detail_view(request, pk):
    """
    The details of a given case.
    """
    issue = _get_issue(request, pk)
    tenancy = _get_tenancy(issue)
    file_urls, image_urls = _get_uploaded_files(issue)
    options = _get_case_detail_options(request, issue)
    context = {
        "issue": issue,
        "tenancy": tenancy,
        "actionstep_url": _get_actionstep_url(issue),
        "notes": _get_issue_notes(request, pk),
        "details": _get_submitted_details(issue),
        "file_urls": file_urls,
        "image_urls": image_urls,
        "people": Person.objects.order_by("full_name").all(),
        "options": options,
    }
    return render(request, "case/case/detail.html", context)


@router.use_route("options")
@paralegal_or_better_required
@require_http_methods(["GET"])
def case_detail_options_view(request, pk):
    issue = _get_issue(request, pk)
    options = _get_case_detail_options(request, issue)
    context = {"options": options, "issue": issue}
    return render(request, "case/case/_detail_options.html", context)


def _get_case_detail_options(request, issue):
    return [
        {**o, "url": reverse(f"case-detail-{slug}", args=(issue.pk,))}
        for slug, o in CASE_DETAIL_OPTIONS.items()
        if o["render_when"](request, issue)
    ]


@router.use_route("note")
@paralegal_or_better_required
@require_http_methods(["GET", "POST"])
def case_detail_note_view(request, pk):
    """
    Form where paralegals can leave notes about case progress.
    """
    view = _build_case_note_view(
        ParalegalNoteForm,
        "note",
        "case/case/forms/_file_note.html",
        "File note created",
        NoteType.PARALEGAL,
    )
    return view(request, pk)


@router.use_route("review")
@coordinator_or_better_required
@require_http_methods(["GET", "POST"])
def case_detail_review_view(request, pk):
    """
    Form where coordinators can leave a note for other coordinators
    """
    view = _build_case_note_view(
        CaseReviewNoteForm,
        "review",
        "case/case/forms/_review_note.html",
        "Review note created",
        NoteType.REVIEW,
    )
    return view(request, pk)


@router.use_route("performance")
@coordinator_or_better_required
@require_http_methods(["GET", "POST"])
def case_detail_performance_view(request, pk):
    """
    Form where coordinators can leave a note on paralegal performance.
    """
    view = _build_case_note_view(
        ParalegalReviewNoteForm,
        "performance",
        "case/case/forms/_paralegal_review_note.html",
        "Review note created",
        NoteType.PERFORMANCE,
    )
    return view(request, pk)


@router.use_route("conflict")
def case_detail_conflict_view(request, pk):
    """
    Form where coordinators can leave a note on paralegal performance.
    """
    view = _build_case_note_view(
        ConflictCheckNoteForm,
        "conflict",
        "case/case/forms/_conflict_check.html",
        "Conflict check record created",
        NoteType.CONFLICT_CHECK,
    )
    return view(request, pk)


def _build_case_note_view(Form, slug, template, success_message, note_type):
    """
    Returns a view that renders a form where you can add a type of note to the case
    """

    def case_note_view(request, pk):
        context = {}
        issue = _get_issue(request, pk)
        if request.method == "POST":
            default_data = {
                "issue": issue,
                "creator": request.user,
                "note_type": note_type,
            }
            form_data = _add_form_data(request.POST, default_data)
            form = Form(form_data)
            if form.is_valid():
                form.save()
                context.update({"notes": _get_issue_notes(request, pk)})
                messages.success(request, success_message)
        else:
            form = Form()

        url = reverse(f"case-detail-{slug}", args=(pk,))
        options_url = reverse("case-detail-options", args=(pk,))
        context.update(
            {"form": form, "issue": issue, "url": url, "options_url": options_url}
        )
        return render(request, template, context)

    return case_note_view


@router.use_route("assign")
@coordinator_or_better_required
@require_http_methods(["GET", "POST"])
def case_detail_assign_view(request, pk):
    """
    Form where coordinators can assign a paralegal to a case
    """
    context = {}
    issue = _get_issue(request, pk)
    if request.method == "POST":
        form = IssueAssignParalegalForm(request.POST, instance=issue)
        if form.is_valid():
            issue = form.save()
            context.update({"new_paralegal": issue.paralegal})
            messages.success(request, "Assignment successful")
    else:
        form = IssueAssignParalegalForm()

    url = reverse(f"case-detail-assign", args=(pk,))
    options_url = reverse(f"case-detail-options", args=(pk,))
    context.update(
        {"form": form, "issue": issue, "url": url, "options_url": options_url}
    )
    return render(request, "case/case/forms/_assign_paralegal.html", context)


@router.use_route("progress")
@paralegal_or_better_required
@require_http_methods(["GET", "POST"])
def case_detail_progress_view(request, pk):
    """
    Form where anyone can progress the case.
    """
    view = _build_case_update_view(
        IssueProgressForm,
        "progress",
        "case/case/forms/_progress.html",
        "Update successful",
    )
    return view(request, pk)


@router.use_route("close")
@coordinator_or_better_required
@require_http_methods(["GET", "POST"])
def case_detail_close_view(request, pk):
    """
    Form where you close the case.
    """
    view = _build_case_update_view(
        IssueCloseForm, "close", "case/case/forms/_close.html", "Case closed!"
    )
    return view(request, pk)


@router.use_route("reopen")
@coordinator_or_better_required
@require_http_methods(["GET", "POST"])
def case_detail_reopen_view(request, pk):
    """
    Form where you reopen the case.
    """
    view = _build_case_update_view(
        IssueReOpenForm, "reopen", "case/case/forms/_reopen.html", "Case re-opened"
    )
    return view(request, pk)


@router.use_route("outcome")
@coordinator_or_better_required
@require_http_methods(["GET", "POST"])
def case_detail_outcome_view(request, pk):
    """
    Form where you update the outcome of the case.
    """
    view = _build_case_update_view(
        IssueOutcomeForm, "outcome", "case/case/forms/_outcome.html", "Outcome updated"
    )
    return view(request, pk)


def _build_case_update_view(Form, slug, template, success_message):
    """
    Returns a view that renders a form where you update the case.
    """

    def case_update_view(request, pk):
        issue = _get_issue(request, pk)
        if request.method == "POST":
            form = Form(request.POST, instance=issue)
            if form.is_valid():
                issue = form.save()
                messages.success(request, success_message)
        else:
            form = Form(instance=issue)

        url = reverse(f"case-detail-{slug}", args=(pk,))
        options_url = reverse(f"case-detail-options", args=(pk,))
        context = {"form": form, "issue": issue, "url": url, "options_url": options_url}
        return render(request, template, context)

    return case_update_view


@router.use_route("agent")
@paralegal_or_better_required
@require_http_methods(["GET", "POST", "DELETE"])
def agent_selet_view(request, pk):
    return _person_select_view(request, pk, "agent")


@router.use_route("landlord")
@paralegal_or_better_required
@require_http_methods(["GET", "POST", "DELETE"])
def landlord_selet_view(request, pk):
    return _person_select_view(request, pk, "landlord")


def _person_select_view(request, pk, person_type):
    issue = _get_issue(request, pk)
    tenancy = _get_tenancy(issue)
    title = "Landlord" if person_type == "landlord" else "Real estate agent"
    context = {
        "title": title,
        "issue": issue,
        "person": None,
        "url_path": f"case-detail-{person_type}",
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


def _get_tenancy(issue):
    # FIXME: Assume only only tenancy but that's not how the models work.
    tenancy = issue.client.tenancy_set.first()
    return tenancy


def _get_issue(request, pk):
    try:
        issue = (
            Issue.objects.check_permisisons(request)
            .select_related("client", "paralegal")
            .prefetch_related("fileupload_set")
            .get(pk=pk)
        )
    except Issue.DoesNotExist:
        raise Http404()

    return issue


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


def _add_form_data(form_data, extra_data):
    return MultiValueDict({**{k: [v] for k, v in extra_data.items()}, **form_data})
