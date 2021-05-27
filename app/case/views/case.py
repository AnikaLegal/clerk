from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import redirect, render
from django.utils.datastructures import MultiValueDict
from django.views.decorators.http import require_http_methods

from case.forms import (
    IssueProgressForm,
    IssueSearchForm,
    ParalegalNoteForm,
    ReviewNoteForm,
)
from core.models import Issue, IssueNote
from core.models.issue_note import NoteType

from django.contrib.auth.decorators import user_passes_test
from .auth import is_superuser


def root_view(request):
    return redirect("case-list")


# FIXME: Permissions
@login_required
@user_passes_test(is_superuser, login_url="/")
@require_http_methods(["GET"])
def case_list_view(request):
    form = IssueSearchForm(request.GET)
    issue_qs = Issue.objects.select_related("client", "paralegal")
    issues = form.search(issue_qs).order_by("-created_at").all()
    page, next_qs, prev_qs = _get_page(request, issues, per_page=14)
    context = {
        "issue_page": page,
        "form": form,
        "next_qs": next_qs,
        "prev_qs": prev_qs,
    }
    return render(request, "case/case_list.html", context)


# FIXME: Permissions
@login_required
@user_passes_test(is_superuser, login_url="/")
@require_http_methods(["GET"])
def case_detail_view(request, pk):
    context = _get_case_detail_context(request, pk)
    return render(request, "case/case_detail.html", context)


# FIXME: Permissions
@login_required
@user_passes_test(is_superuser, login_url="/")
@require_http_methods(["GET"])
def case_detail_progress_view(request, pk):
    context = _get_case_detail_context(request, pk)
    notes = _get_issue_notes(pk)
    context = {
        **context,
        "notes": notes,
        "progress_form": IssueProgressForm(instance=context["issue"]),
        "case_review_form": ReviewNoteForm(),
        "paralegal_notes_form": ParalegalNoteForm(),
    }
    return render(request, "case/case_detail_progress.html", context)


# FIXME: Permissions
@login_required
@user_passes_test(is_superuser, login_url="/")
@require_http_methods(["POST"])
def case_detail_review_note_form_view(request, pk):
    context = _get_case_detail_context(request, pk)
    default_data = {
        "issue": context["issue"],
        "creator": request.user,
        "note_type": NoteType.REVIEW,
    }
    form_data = _add_form_data(request.POST, default_data)
    form = ReviewNoteForm(form_data)
    notes = None
    if form.is_valid():
        form.save()
        notes = _get_issue_notes(pk)
        messages.success(request, "Note created")

    context = {**context, "form": form, "htmx_notes": notes}
    return render(request, "case/htmx/_case_review_note_form.html", context)


# FIXME: Permissions
@login_required
@user_passes_test(is_superuser, login_url="/")
@require_http_methods(["POST"])
def case_detail_paralegal_note_form_view(request, pk):
    context = _get_case_detail_context(request, pk)
    default_data = {
        "issue": context["issue"],
        "creator": request.user,
        "note_type": NoteType.PARALEGAL,
    }
    form_data = _add_form_data(request.POST, default_data)
    form = ParalegalNoteForm(form_data)
    notes = None
    if form.is_valid():
        form.save()
        notes = _get_issue_notes(pk)
        messages.success(request, "Note created")

    context = {**context, "form": form, "htmx_notes": notes}
    return render(request, "case/htmx/_case_paralegal_note_form.html", context)


# FIXME: Permissions
@login_required
@user_passes_test(is_superuser, login_url="/")
@require_http_methods(["POST"])
def case_detail_progress_form_view(request, pk):
    context = _get_case_detail_context(request, pk)
    form = IssueProgressForm(request.POST, instance=context["issue"])
    if form.is_valid():
        form.save()
        messages.success(request, "Update successful")

    context = {**context, "form": form}
    return render(request, "case/htmx/_case_progress_form.html", context)


def _get_issue_notes(pk):
    return (
        IssueNote.objects.filter(issue=pk)
        .select_related("creator")
        .order_by("-created_at")
        .all()
    )


def _get_case_detail_context(request, pk):
    try:
        # FIXME: Who has access to this?
        issue = Issue.objects.select_related("client").get(pk=pk)
    except Issue.DoesNotExist:
        raise Http404()

    # FIXME: Assume only only tenancy but that's not how the models work.
    tenancy = issue.client.tenancy_set.first()

    if issue.actionstep_id:
        actionstep_url = _get_actionstep_url(issue.actionstep_id)
    else:
        actionstep_url = None

    return {
        "issue": issue,
        "tenancy": tenancy,
        "actionstep_url": actionstep_url,
    }


def _get_page(request, items, per_page):
    page_number = request.GET.get("page", 1) or 1
    paginator = Paginator(items, per_page=per_page)
    page = paginator.get_page(page_number)
    next_page_num = page.next_page_number() if page.has_next() else paginator.num_pages
    prev_page_num = page.previous_page_number() if page.has_previous() else 1
    get_query = {k: v for k, v in request.GET.items()}
    next_qs = "?" + urlencode({**get_query, "page": next_page_num})
    prev_qs = "?" + urlencode({**get_query, "page": prev_page_num})
    return page, next_qs, prev_qs


def _get_actionstep_url(actionstep_id):
    return f"https://ap-southeast-2.actionstep.com/mym/asfw/workflow/action/overview/action_id/{actionstep_id}"


def _add_form_data(form_data, extra_data):
    return MultiValueDict({**{k: [v] for k, v in extra_data.items()}, **form_data})
