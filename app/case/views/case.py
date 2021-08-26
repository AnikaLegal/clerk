from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Max
from django.utils import timezone

from case.forms import (
    IssueProgressForm,
    IssueSearchForm,
    ParalegalNoteForm,
    CaseReviewNoteForm,
    IssueAssignParalegalForm,
    IssueOpenForm,
    ParalegalReviewNoteForm,
)
from case.utils import Selector, HtmxFormView, get_page
from core.models import Issue, IssueNote
from core.models.issue import CaseStage
from core.models.issue_note import NoteType

from .auth import (
    login_required,
    paralegal_or_better_required,
    coordinator_or_better_required,
)

COORDINATORS_EMAIL = "coordinators@anikalegal.com"


@require_http_methods(["GET"])
def root_view(request):
    return redirect("case-list")


@login_required
@require_http_methods(["GET"])
def not_allowed_view(request):
    return render(request, "case/not_allowed.html")


@coordinator_or_better_required
@require_http_methods(["GET"])
def case_review_view(request):
    """Inbox page where coordinators can see new cases for them to review and assign"""
    is_open = Q(is_open=True)
    has_review = Q(issuenote__note_type=NoteType.REVIEW)
    is_review = is_open & has_review
    issues = (
        Issue.objects.select_related("client", "paralegal")
        .prefetch_related("issuenote_set")
        .filter(is_review)
        .annotate(next_review=Max("issuenote__event"))
        .order_by("next_review")
    )
    # Annotate issues with days from now
    now = timezone.now()
    for issue in issues:
        days = (issue.next_review - now).days
        if days >= 7:
            issue.color = ""
        elif days >= 3:
            issue.color = "green"
        elif days >= 2:
            issue.color = "yellow"
        elif days >= 0:
            issue.color = "orange"
        else:
            issue.color = "red"

    context = {"issues": issues}
    return render(request, "case/case_review.html", context)


@coordinator_or_better_required
@require_http_methods(["GET"])
def case_inbox_view(request):
    """Inbox page where coordinators can see new cases for them to review and assign"""
    is_coordinators = Q(paralegal__email=COORDINATORS_EMAIL)
    is_open = Q(is_open=True)
    is_new_stage = Q(stage=CaseStage.UNSTARTED) | Q(stage__isnull=True)
    is_inbox = is_coordinators & is_open & is_new_stage
    issues = Issue.objects.select_related("client", "paralegal").filter(is_inbox)
    context = {"issues": issues}
    return render(request, "case/case_inbox.html", context)


@login_required
@require_http_methods(["GET"])
def case_list_view(request):
    """
    List of all cases for paralegals and coordinators to view.
    """
    form = IssueSearchForm(request.GET)
    issue_qs = Issue.objects.select_related("client", "paralegal")

    if request.user.is_paralegal:
        # Paralegals can only see assigned cases
        issue_qs = issue_qs.filter(paralegal=request.user)
    elif not request.user.is_coordinator_or_better:
        issue_qs = issue_qs.none()

    issues = form.search(issue_qs).order_by("-created_at").all()
    page, next_qs, prev_qs = get_page(request, issues, per_page=28)
    context = {
        "issue_page": page,
        "form": form,
        "next_qs": next_qs,
        "prev_qs": prev_qs,
    }
    return render(request, "case/case_list.html", context)


class CaseReviewHtmxFormView(HtmxFormView):
    """
    Form where coordinators can leave a note for other coordinators
    """

    template = "case/htmx/_case_review_note_form.html"
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

    template = "case/htmx/_paralegal_review_note_form.html"
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

    template = "case/htmx/_case_paralegal_note_form.html"
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

    template = "case/htmx/_assign_paralegal_form.html"
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

    template = "case/htmx/_case_progress_form.html"
    success_message = "Update successful"
    form_cls = IssueProgressForm

    def is_user_allowed(self, request):
        return request.user.is_paralegal_or_better

    def get_form_instance(self, request, context, *args, **kwargs):
        return context["issue"]


class CaseOpenHtmxFormView(HtmxFormView):
    """
    Form where you can open or close the case.
    """

    template = "case/htmx/_case_open_form.html"
    success_message = "Update successful"
    form_cls = IssueOpenForm

    def is_user_allowed(self, request):
        return request.user.is_coordinator_or_better

    def get_form_instance(self, request, context, *args, **kwargs):
        return context["issue"]


class CaseSelector(Selector):
    """
    A drop down where users can select the actions that they want to take for a case.
    """

    slug = "case"
    default_text = "I want to..."
    child_views = {
        "note": FileNoteHtmxFormView(),
        "review": CaseReviewHtmxFormView(),
        "assign": AssignParalegalHtmxFormView(),
        "progress": CaseProgressHtmxFormView(),
        "open": CaseOpenHtmxFormView(),
        "performance": ParalegalReviewHtmxFormView(),
    }
    render_when = {
        k: lambda view, request: view.is_user_allowed(request)
        for k in ("note", "review", "progress", "assign", "open", "performance")
    }
    options = {
        "note": "Add a file note",
        "review": "Add a coordinator's case review note",
        "performance": "Add a paralegal performance review note",
        "assign": "Assign a paralegal to the case",
        "progress": "Progress case status",
        "open": "Close or re-open the case",
    }


@paralegal_or_better_required
@require_http_methods(["GET", "POST"])
def case_detail_view(request, pk, form_slug=""):
    """
    The details of a given case.
    """
    try:
        issue_qs = Issue.objects.select_related("client").prefetch_related(
            "fileupload_set"
        )
        if request.user.is_paralegal:
            # Paralegals can only see cases that they are assigned to
            issue_qs.filter(paralegal=request.user)

        issue = issue_qs.get(pk=pk)
    except Issue.DoesNotExist:
        raise Http404()

    # FIXME: Assume only only tenancy but that's not how the models work.
    tenancy = issue.client.tenancy_set.first()
    case_selector = CaseSelector(request)

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
    }
    form_view = case_selector.handle(form_slug, context, pk)
    if form_view:
        return form_view
    else:
        return render(request, "case/case_detail.html", context)


MAYBE_IMAGE_FILE_EXTENSIONS = [".png", ".jpg", ".jpeg"]


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
