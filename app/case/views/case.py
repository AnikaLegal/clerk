from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import redirect, render
from django.utils.datastructures import MultiValueDict
from django.views.decorators.http import require_http_methods
from django.forms import Form

from case.forms import (
    IssueProgressForm,
    IssueSearchForm,
    ParalegalNoteForm,
    ReviewNoteForm,
)
from case.utils import Selector
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


class HtmxFormView:
    template: str
    success_message: str
    form_cls: Form

    def __call__(self, request, context, *args, **kwargs):
        if request.method == "GET":
            return self.get(request, context, *args, **kwargs)
        elif request.method == "POST":
            return self.post(request, context, *args, **kwargs)

    def get(self, request, context, *args, **kwargs):
        instance = self.get_form_instance(request, context, *args, **kwargs)
        form = self.form_cls(instance=instance)
        context = {**context, "form": form}
        return render(request, self.template, context)

    def post(self, request, context, *args, **kwargs):
        instance = self.get_form_instance(request, context, *args, **kwargs)
        default_data = self.get_default_form_data(request, context, *args, **kwargs)
        form_data = _add_form_data(request.POST, default_data)
        form = self.form_cls(data=form_data, instance=instance)
        if form.is_valid():
            form.save()
            success_context = self.get_success_context(context, *args, **kwargs)
            context.update(success_context)
            messages.success(request, self.success_message)

        context = {**context, "form": form}
        return render(request, self.template, context)

    def get_success_context(self, context, *args, **kwargs):
        return context

    def get_default_form_data(self, request, context, *args, **kwargs):
        return {}

    def get_form_instance(self, request, context, *args, **kwargs):
        return None


# FIXME: Permissions
class ReviewNoteHtmxFormView(HtmxFormView):
    template = "case/htmx/_case_review_note_form.html"
    success_message = "Note created"
    form_cls = ReviewNoteForm

    def get_success_context(self, context, pk, *args, **kwargs):
        return {"notes": _get_issue_notes(pk)}

    def get_default_form_data(self, request, context, *args, **kwargs):
        return {
            "issue": context["issue"],
            "creator": request.user,
            "note_type": NoteType.REVIEW,
        }


# FIXME: Permissions
class ParalegalNoteHtmxFormView(HtmxFormView):
    template = "case/htmx/_case_paralegal_note_form.html"
    success_message = "Note created"
    form_cls = ParalegalNoteForm

    def get_success_context(self, context, pk, *args, **kwargs):
        return {"notes": _get_issue_notes(pk)}

    def get_default_form_data(self, request, context, *args, **kwargs):
        return {
            "issue": context["issue"],
            "creator": request.user,
            "note_type": NoteType.PARALEGAL,
        }


# FIXME: Permissions
class CaseProgressHtmxFormView(HtmxFormView):
    template = "case/htmx/_case_progress_form.html"
    success_message = "Update successful"
    form_cls = IssueProgressForm

    def get_success_context(self, context, pk, *args, **kwargs):
        return {"notes": _get_issue_notes(pk)}

    def get_default_form_data(self, request, context, *args, **kwargs):
        return {
            "issue": context["issue"],
            "creator": request.user,
            "note_type": NoteType.PARALEGAL,
        }

    def get_form_instance(self, request, context, *args, **kwargs):
        return context["issue"]


case_selector = Selector(
    slug="case",
    default_text="I want to...",
    child_views={
        "note": ParalegalNoteHtmxFormView(),
        "review": ReviewNoteHtmxFormView(),
        "progress": CaseProgressHtmxFormView(),
    },
    options={
        "note": "Write a case note",
        "review": "Write a paralegal review note",
        "progress": "Update case progress",
    },
)


# FIXME: Permissions
@login_required
@user_passes_test(is_superuser, login_url="/")
@require_http_methods(["GET", "POST"])
def case_detail_view(request, pk, form_slug=""):
    try:
        # FIXME: Who has access to this?
        issue = Issue.objects.select_related("client").get(pk=pk)
    except Issue.DoesNotExist:
        raise Http404()

    # FIXME: Assume only only tenancy but that's not how the models work.
    tenancy = issue.client.tenancy_set.first()
    context = {
        "issue": issue,
        "tenancy": tenancy,
        "actionstep_url": _get_actionstep_url(issue),
        "notes": _get_issue_notes(pk),
        "case_selector": case_selector,
    }
    form_view = case_selector.handle(request, form_slug, context, pk)
    if form_view:
        return form_view
    else:
        return render(request, "case/case_detail.html", context)


def _get_issue_notes(pk):
    return (
        IssueNote.objects.filter(issue=pk)
        .select_related("creator")
        .order_by("-created_at")
        .all()
    )


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


def _get_actionstep_url(issue):
    if issue.actionstep_id:
        return f"https://ap-southeast-2.actionstep.com/mym/asfw/workflow/action/overview/action_id/{issue.actionstep_id}"


def _add_form_data(form_data, extra_data):
    return MultiValueDict({**{k: [v] for k, v in extra_data.items()}, **form_data})
