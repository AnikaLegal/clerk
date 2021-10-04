import re
import os

from django.http import Http404
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.utils.html import strip_tags
from html_sanitizer import Sanitizer

from core.models import Issue
from case.views.auth import paralegal_or_better_required
from emails.service import build_clerk_address
from emails.models import EmailState, Email
from case.forms import EmailForm
from case.utils import merge_form_data
from case.utils.router import Router


DISPLAY_EMAIL_STATES = [EmailState.SENT, EmailState.INGESTED]
DRAFT_EMAIL_STATES = [EmailState.READY_TO_SEND, EmailState.DRAFT]

router = Router("email")
router.create_route("list").uuid("pk")
router.create_route("draft").uuid("pk").path("draft")
router.create_route("edit").uuid("pk").path("draft").pk("email_pk")
router.create_route("send").uuid("pk").path("draft").pk("email_pk").path("send")
(
    router.create_route("attach")
    .uuid("pk")
    .path("draft")
    .pk("email_pk")
    .path("attachment")
    .pk("attach_pk", optional=True)
)


@router.use_route("list")
@paralegal_or_better_required
@require_http_methods(["GET"])
def email_list_view(request, pk):
    issue = _get_issue_for_emails(request, pk)
    case_email_address = build_clerk_address(issue)
    email_qs = issue.email_set.prefetch_related("emailattachment_set").order_by(
        "-created_at"
    )
    display_emails = email_qs.filter(state__in=DISPLAY_EMAIL_STATES)
    draft_emails = email_qs.filter(state__in=DRAFT_EMAIL_STATES)
    for emails in [display_emails, draft_emails]:
        for email in emails:
            email.html = get_email_html(email)
            for attachment in email.emailattachment_set.all():
                attachment.file.display_name = os.path.basename(attachment.file.name)

    context = {
        "issue": issue,
        "display_emails": display_emails,
        "draft_emails": draft_emails,
        "case_email_address": case_email_address,
    }
    return render(request, "case/case/email/list.html", context)


@router.use_route("draft")
@paralegal_or_better_required
@require_http_methods(["GET", "POST"])
def email_draft_create_view(request, pk):
    issue = _get_issue_for_emails(request, pk)
    case_email_address = build_clerk_address(issue, email_only=True)
    case_emails = get_case_emails(issue)
    if request.method == "POST":
        default_data = {
            "from_address": case_email_address,
            "state": EmailState.DRAFT,
            "issue": issue,
            "sender": request.user,
        }
        data = merge_form_data(request.POST, default_data)
        form = EmailForm(data, files=request.FILES)
        if form.is_valid():
            email = form.save()
            messages.success(request, "Draft created")
            return redirect("case-email-edit", issue.pk, email.pk)
    else:
        form = EmailForm()

    context = {
        "issue": issue,
        "form": form,
        "case_emails": case_emails,
        "case_email_address": case_email_address,
        "is_disabled": False,
    }
    return render(request, "case/case/email/draft_create.html", context)


@router.use_route("edit")
@paralegal_or_better_required
@require_http_methods(["GET", "POST"])
def email_draft_edit_view(request, pk, email_pk):
    issue = _get_issue_for_emails(request, pk)
    email = _get_email_for_issue(issue, email_pk)
    if not email.state in DRAFT_EMAIL_STATES:
        return redirect("case-email-list", issue.pk)

    case_email_address = build_clerk_address(issue, email_only=True)
    case_emails = get_case_emails(issue)
    if request.method == "POST":
        default_data = {
            "from_address": case_email_address,
            "state": EmailState.DRAFT,
            "issue": issue,
            "sender": request.user,
        }
        data = merge_form_data(request.POST, default_data)
        form = EmailForm(data, instance=email, files=request.FILES)
        if form.is_valid():
            messages.success(request, "Draft saved.")
            email = form.save()

    else:
        form = EmailForm(instance=email)

    context = {
        "issue": issue,
        "form": form,
        "case_emails": case_emails,
        "email": email,
        "case_email_address": case_email_address,
        "is_disabled": email.state != EmailState.DRAFT,
    }
    return render(request, "case/case/email/draft_edit.html", context)


@router.use_route("send")
@paralegal_or_better_required
@require_http_methods(["POST"])
def email_draft_send_view(request, pk, email_pk):
    issue = _get_issue_for_emails(request, pk)
    email = _get_email_for_issue(issue, email_pk)
    if not email.state == EmailState.DRAFT:
        raise Http404()

    email.state = EmailState.READY_TO_SEND
    email.save()
    form = EmailForm(instance=email)
    context = {
        "issue": issue,
        "form": form,
        "email": email,
        "is_disabled": True,
    }
    return render(request, "case/case/email/_email_form.html", context)


@router.use_route("attach")
@paralegal_or_better_required
@require_http_methods(["DELETE"])
def email_attachment_delete_view(request, pk, email_pk, attach_pk):
    issue = _get_issue_for_emails(request, pk)
    email = _get_email_for_issue(issue, email_pk)
    if not email.state == EmailState.DRAFT:
        raise Http404()

    email.emailattachment_set.filter(id=attach_pk).delete()
    context = {"issue": issue, "email": email}
    return render(request, "case/case/email/_draft_attachments.html", context)


def _get_email_for_issue(issue, email_pk):
    try:
        return issue.email_set.get(pk=email_pk)
    except Email.DoesNotExist:
        raise Http404()


def _get_issue_for_emails(request, pk):
    try:
        return (
            Issue.objects.check_permisisons(request)
            .prefetch_related("email_set")
            .get(pk=pk)
        )
    except Issue.DoesNotExist:
        raise Http404()


def get_case_emails(issue: Issue):
    tenancy = issue.client.tenancy_set.select_related("landlord", "agent").first()
    emails = [
        {
            "email": issue.client.email,
            "name": issue.client.get_full_name(),
            "role": "Client",
        }
    ]
    if tenancy.agent:
        emails.append(
            {
                "email": tenancy.agent.email,
                "name": tenancy.agent.full_name,
                "role": "Agent",
            }
        )
    if tenancy.landlord:
        emails.append(
            {
                "email": tenancy.landlord.email,
                "name": tenancy.landlord.full_name,
                "role": "Landlord",
            }
        )

    return emails


sanitizer = Sanitizer(
    {
        "tags": {
            "a",
            "b",
            "blockquote",
            "br",
            "div",
            "em",
            "h1",
            "h2",
            "h3",
            "hr",
            "i",
            "li",
            "ol",
            "p",
            "span",
            "strong",
            "sub",
            "sup",
            "ul",
            "img",
        },
        "attributes": {
            "a": ("href", "name", "target", "title", "id", "rel", "src", "style")
        },
        "empty": {"hr", "a", "br"},
        "separate": {"a", "p", "li"},
        "whitespace": {"br"},
        "keep_typographic_whitespace": False,
        "add_nofollow": False,
        "autolink": False,
    }
)


def get_email_html(email) -> str:
    if email.html:
        return sanitizer.sanitize(email.html)
    else:
        text = email.text.replace("\r", "")
        text = re.sub("\n(?!\n)", " <br/>", text)
        return "".join(
            [f"<p>{line}</p>" for line in strip_tags(text).split("\n") if line]
        )
