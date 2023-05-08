import re
import os
from typing import List
from django.utils.text import slugify

from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods
from django.utils.html import strip_tags
from html_sanitizer import Sanitizer
from django.urls import reverse
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.db.models import Q
from django.db import transaction
from django.core.files.base import ContentFile
from bs4 import BeautifulSoup
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from core.models import Issue
from case.views.auth import paralegal_or_better_required
from emails.service import build_clerk_address
from emails.models import (
    EmailState,
    Email,
    EmailTemplate,
    EmailAttachment,
    SharepointState,
)
from case.utils.router import Router
from microsoft.endpoints import MSGraphAPI
from microsoft.service import save_email_attachment
from case.utils.react import render_react_page
from case.serializers import (
    IssueDetailSerializer,
    EmailSerializer,
    EmailAttachmentSerializer,
    EmailTemplateSerializer,
    EmailThreadSerializer,
)
from case.views.case.detail import get_detail_urls


DISPLAY_EMAIL_STATES = [EmailState.SENT, EmailState.INGESTED]
DRAFT_EMAIL_STATES = [EmailState.READY_TO_SEND, EmailState.DRAFT]

router = Router("email")
router.create_route("list").uuid("pk")
router.create_route("thread").uuid("pk").path("thread").slug("slug")
router.create_route("draft").uuid("pk").path("draft")
router.create_route("edit").uuid("pk").path("draft").pk("email_pk")
router.create_route("send").uuid("pk").path("draft").pk("email_pk").path("send")
router.create_route("preview").uuid("pk").path("draft").pk("email_pk").path("preview")
(
    router.create_route("attach")
    .uuid("pk")
    .path("draft")
    .pk("email_pk")
    .path("attachment")
    .pk("attach_pk", optional=True)
)
router.create_route("attach-upload").uuid("pk").pk("email_pk").pk("attach_pk")


@router.use_route("list")
@paralegal_or_better_required
@require_http_methods(["GET"])
def email_list_view(request, pk):
    issue = _get_issue_for_emails(request, pk)
    case_email_address = build_clerk_address(issue)
    email_threads = _get_email_threads(issue)
    context = {
        "issue": IssueDetailSerializer(issue).data,
        "email_threads": EmailThreadSerializer(email_threads, many=True).data,
        "case_email_address": case_email_address,
        "urls": get_detail_urls(issue),
        "draft_url": reverse("case-email-draft", args=(issue.pk,)),
    }
    return render_react_page(request, f"Case {issue.fileref}", "email-list", context)


@router.use_route("thread")
@paralegal_or_better_required
@require_http_methods(["GET"])
def email_thread_view(request, pk, slug):
    issue = _get_issue_for_emails(request, pk)
    case_email_address = build_clerk_address(issue)
    email_threads = [t for t in _get_email_threads(issue) if t.slug == slug]
    if email_threads:
        # Assume thread slugs are unique.
        email_thread = email_threads[0]
    else:
        raise Http404()
    context = {
        "issue": IssueDetailSerializer(issue).data,
        "subject": email_thread.subject,
        "emails": EmailSerializer(email_thread.emails, many=True).data,
        "case_email_address": case_email_address,
        "case_email_list_url": reverse("case-email-list", args=(issue.pk,)),
    }
    return render_react_page(request, f"Case {issue.fileref}", "email-thread", context)


class EmailThread:
    def __init__(self, email: Email):
        self.emails = [email]
        self.issue = email.issue
        self.subject = email.subject or "No Subject"
        self.slug = self.slugify_subject(self.subject)
        self.most_recent = email.created_at

    @staticmethod
    def slugify_subject(subject):
        sub = subject or ""
        sub_cleaned = re.sub(r"re\s*:\s*", "", sub, flags=re.IGNORECASE)
        sub_cleaned = sub_cleaned or "No Subject"
        return slugify(sub_cleaned)

    def is_email_in_thread(self, email: Email) -> bool:
        return self.slug == self.slugify_subject(email.subject)

    def add_email_if_in_thread(self, email: Email) -> bool:
        is_in_thread = self.is_email_in_thread(email)
        if is_in_thread:
            self.emails.append(email)
            if email.created_at > self.most_recent:
                self.most_recent = email.created_at

        return is_in_thread

    def __repr__(self):
        return f"EmailThread<{self.subject}>"


DISPLAY_EMAIL_STATES = [
    EmailState.DRAFT,
    EmailState.SENT,
    EmailState.INGESTED,
    EmailState.DELIVERED,
    EmailState.DELIVERY_FAILURE,
]


def _get_email_threads(issue) -> List[EmailThread]:
    email_qs = (
        issue.email_set.filter(state__in=DISPLAY_EMAIL_STATES)
        .prefetch_related("emailattachment_set")
        .order_by("created_at")
    )
    threads = []
    for email in email_qs:
        _process_email_for_display(email)

        # Assign each email to a thread
        is_in_a_thread = False
        for thread in threads:
            is_in_a_thread = thread.add_email_if_in_thread(email)
            if is_in_a_thread:
                break

        if not is_in_a_thread:
            threads.append(EmailThread(email))

    for thread in threads:
        thread.emails = sorted(thread.emails, key=lambda t: t.created_at, reverse=True)

    return sorted(threads, key=lambda t: t.most_recent, reverse=True)


IMAGE_SUFFIXES = [".jpg", ".jpeg", ".png", ".gif"]


def _process_email_for_display(email: Email):
    email.html = get_email_html(email)
    for attachment in email.emailattachment_set.all():
        attachment.file.display_name = os.path.basename(attachment.file.name)


@router.use_route("draft")
@paralegal_or_better_required
@api_view(["GET", "POST"])
def email_draft_create_view(request, pk):
    issue = _get_issue_for_emails(request, pk)
    if request.method == "POST":
        data = {
            "from_address": build_clerk_address(issue, email_only=True),
            "state": EmailState.DRAFT,
            "sender": request.user,
            **request.data,
        }
        serializer = EmailSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(issue=issue)
        return Response(serializer.data)
    else:
        templates = EmailTemplate.objects.filter(
            Q(topic=issue.topic) | Q(topic="GENERAL")
        ).order_by("created_at")
        parent_id = request.GET.get("parent")
        parent_email = None
        if parent_id:
            try:
                parent_email = EmailSerializer(Email.objects.get(pk=parent_id)).data
            except Email.DoesNotExist:
                raise Http404()

        context = {
            "case_email_url": reverse("case-email-list", args=(issue.pk,)),
            "parent_email": parent_email,
            "issue": IssueDetailSerializer(issue).data,
            "templates": EmailTemplateSerializer(templates, many=True).data,
        }
        return render_react_page(
            request, f"Case {issue.fileref}", "email-draft-create", context
        )


@router.use_route("edit")
@paralegal_or_better_required
@api_view(["GET", "PATCH", "DELETE"])
def email_draft_edit_view(request, pk, email_pk):
    issue = _get_issue_for_emails(request, pk)
    email = _get_email_for_issue(issue, email_pk)
    if not email.state in DRAFT_EMAIL_STATES:
        return redirect("case-email-list", issue.pk)
    if request.method == "PATCH":
        serializer = EmailSerializer(email, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    elif request.method == "DELETE":
        with transaction.atomic():
            email.emailattachment_set.all().delete()
            email.delete()
        return Response({})
    else:
        # GET request.
        api = MSGraphAPI()
        sharepoint_docs = api.folder.get_all_files(f"cases/{issue.id}")
        context = {
            "email_preview_url": reverse(
                "case-email-preview", args=(issue.pk, email.pk)
            ),
            "case_email_url": reverse("case-email-list", args=(issue.pk,)),
            "issue": IssueDetailSerializer(issue).data,
            "email": EmailSerializer(email).data,
            "sharepoint_docs": sharepoint_docs,
        }
        return render_react_page(
            request, f"Case {issue.fileref}", "email-draft-edit", context
        )


@router.use_route("send")
@paralegal_or_better_required
@api_view(["POST"])
def email_draft_send_view(request, pk, email_pk):
    issue = _get_issue_for_emails(request, pk)
    email = _get_email_for_issue(issue, email_pk)
    if email.state == EmailState.DRAFT:
        email.state = EmailState.READY_TO_SEND
        email.html = _render_email_template(email.html)
        email.save()
    else:
        raise Http404()

    return Response(status=200)


@router.use_route("preview")
@paralegal_or_better_required
@require_http_methods(["GET"])
def email_draft_preview_view(request, pk, email_pk):
    issue = _get_issue_for_emails(request, pk)
    email = _get_email_for_issue(issue, email_pk)
    if not email.state in DRAFT_EMAIL_STATES:
        return redirect("case-email-list", issue.pk)

    html = _render_email_template(email.html)
    return HttpResponse(html, "text/html", 200)


def _render_email_template(html):
    if html:
        soup = BeautifulSoup(html, parser="lxml", features="lxml")
        for p_tag in soup.find_all("p"):
            p_tag["style"] = "margin:0 0 12px 0;"

        for a_tag in soup.find_all("a"):
            a_tag["style"] = "color:#438fef;text-decoration:underline;"

        context = {"html": mark_safe(soup.body.decode_contents())}
    else:
        context = {"html": ""}
    return render_to_string("case/case/email_preview.html", context)


@router.use_route("attach")
@paralegal_or_better_required
@api_view(["POST", "DELETE"])
def email_attachment_view(request, pk, email_pk, attach_pk=None):
    """Delete the email attachment, return HTML fragment for htmx."""
    issue = _get_issue_for_emails(request, pk)
    email = _get_email_for_issue(issue, email_pk)
    if not email.state == EmailState.DRAFT:
        raise Http404()

    if request.method == "DELETE":
        email.emailattachment_set.filter(id=attach_pk).delete()
        return Response(status=200)

    else:
        # POST request.
        if "sharepoint_id" in request.data:
            # Download attachment from SharePoint.
            sharepoint_id = request.data["sharepoint_id"]
            api = MSGraphAPI()
            filename, content_type, file_bytes = api.folder.download_file(sharepoint_id)
            # Save as email attachment
            f = ContentFile(file_bytes, name=filename)
        elif "file" in request.data:
            f = request.data["file"]
            content_type = f.content_type
        else:
            msg = "Could not find and uploaded file or SharePoint document."
            raise ValidationError(msg)

        if f.size / 1024 / 1024 > 30:
            raise ValidationError({"file": "File must be <30MB."})

        attach = EmailAttachment.objects.create(
            email=email,
            file=f,
            content_type=content_type,
        )
        serializer = EmailAttachmentSerializer(attach)
        return Response(serializer.data)


@router.use_route("attach-upload")
@paralegal_or_better_required
@api_view(["POST"])
def email_attachment_upload_view(request, pk, email_pk, attach_pk):
    """Save the attachment to Sharepoint"""
    issue = _get_issue_for_emails(request, pk)
    email = _get_email_for_issue(issue, email_pk)
    try:
        attachment = EmailAttachment.objects.get(pk=attach_pk)
    except EmailAttachment.DoesNotExist:
        raise Http404()

    attachment.sharepoint_state = SharepointState.UPLOADING
    attachment.save()
    save_email_attachment(email, attachment)
    attachment.sharepoint_state = SharepointState.UPLOADED
    attachment.save()
    return Response(data=EmailAttachmentSerializer(instance=attachment).data)


def _get_email_for_issue(issue, email_pk):
    try:
        return issue.email_set.get(pk=email_pk)
    except Email.DoesNotExist:
        raise Http404()


def _get_issue_for_emails(request, pk):
    try:
        return (
            Issue.objects.check_permissions(request)
            .prefetch_related("email_set__emailattachment_set")
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
        "empty": {"hr", "a", "br", "div"},
        "separate": {"a", "p", "li", "div"},
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
        text = re.sub("\n(?!\n)", "<br/>", text)
        return "".join(
            [f"<p>{line}</p>" for line in strip_tags(text).split("\n") if line]
        )
