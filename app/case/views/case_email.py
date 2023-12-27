import os
from typing import List

from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.db.models import Q
from django.db import transaction
from django.core.files.base import ContentFile
from bs4 import BeautifulSoup
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (
    RetrieveModelMixin,
    DestroyModelMixin,
)
from django.shortcuts import get_object_or_404

from emails.utils.threads import EmailThread
from emails.utils.html import get_email_html
from core.models import Issue
from case.views.auth import (
    paralegal_or_better_required,
    CoordinatorOrBetterPermission,
    ParalegalOrBetterObjectPermission,
)
from emails.service import build_clerk_address
from emails.models import (
    EmailState,
    Email,
    EmailTemplate,
    EmailAttachment,
    SharepointState,
)
from microsoft.endpoints import MSGraphAPI
from microsoft.service import save_email_attachment
from case.utils.react import render_react_page
from case.serializers import (
    IssueSerializer,
    EmailSerializer,
    EmailAttachmentSerializer,
    EmailTemplateSerializer,
    EmailThreadSerializer,
)
from case.views.case import get_detail_urls


DRAFT_EMAIL_STATES = [EmailState.READY_TO_SEND, EmailState.DRAFT]
DISPLAY_EMAIL_STATES = [
    EmailState.DRAFT,
    EmailState.SENT,
    EmailState.INGESTED,
    EmailState.DELIVERED,
    EmailState.DELIVERY_FAILURE,
]


@require_http_methods(["GET"])
@paralegal_or_better_required
def email_list_page_view(request, pk):
    issue = get_object_or_404(Issue, pk=pk)
    case_email_address = build_clerk_address(issue)
    context = {
        "case_pk": pk,
        "urls": get_detail_urls(issue),
        "case_email_address": case_email_address,
        "draft_url": reverse("case-email-draft", args=(issue.pk,)),
    }
    return render_react_page(request, f"Case {issue.fileref}", "email-list", context)


@require_http_methods(["GET"])
@paralegal_or_better_required
def email_thread_page_view(request, pk, slug):
    issue = get_object_or_404(Issue, pk=pk)
    case_email_address = build_clerk_address(issue)
    context = {
        "case_pk": pk,
        "case_email_address": case_email_address,
        "case_email_list_url": reverse("case-email-list", args=(issue.pk,)),
    }
    return render_react_page(request, f"Case {issue.fileref}", "email-thread", context)


@api_view(["GET"])
@paralegal_or_better_required
def email_draft_create_page_view(request, pk):
    issue = get_object_or_404(Issue, pk=pk)
    templates = EmailTemplate.objects.filter(
        Q(topic=issue.topic) | Q(topic="GENERAL")
    ).order_by("created_at")
    parent_email_id = request.GET.get("parent")
    context = {
        "case_pk": pk,
        "parent_email_id": parent_email_id,
        "case_email_url": reverse("case-email-list", args=(issue.pk,)),
        "templates": EmailTemplateSerializer(templates, many=True).data,
    }
    return render_react_page(
        request, f"Case {issue.fileref}", "email-draft-create", context
    )


@api_view(["GET"])
@paralegal_or_better_required
def email_draft_edit_page_view(request, pk, email_pk):
    issue = get_object_or_404(Issue, pk=pk)
    context = {
        "email_preview_url": reverse("case-email-preview", args=(issue.pk, email_pk)),
        "case_email_url": reverse("case-email-list", args=(issue.pk,)),
    }
    return render_react_page(
        request, f"Case {issue.fileref}", "email-draft-edit", context
    )


# FIXME: IMPLEMENT PROPERLY
@require_http_methods(["GET"])
@paralegal_or_better_required
def email_draft_preview_page_view(request, pk, email_pk):
    # issue = _get_issue_for_emails(request, pk)
    # email = _get_email_for_issue(issue, email_pk)
    if not email.state in DRAFT_EMAIL_STATES:
        return redirect("case-email-list", issue.pk)

    html = _render_email_template(email.html)
    return HttpResponse(html, "text/html", 200)


class EmailApiViewset(GenericViewSet):
    permission_classes = [
        CoordinatorOrBetterPermission | ParalegalOrBetterObjectPermission
    ]

    def get_queryset(self):
        user = self.request.user
        queryset = Issue.objects.prefetch_related("email_set__emailattachment_set")
        if user.is_paralegal:
            # Paralegals can only see assigned cases
            queryset = queryset.filter(paralegal=user)
        elif not user.is_coordinator_or_better:
            # If you're not a paralegal or coordinator you can't see nuthin.
            queryset = queryset.none()

        return queryset

    def retrieve(self, request, *args, **kwargs):
        """Fetch all email threads for a given issue"""
        issue = self.get_object()
        email_threads = get_email_threads(issue)
        slug = request.query_params.get("slug")
        if slug:
            email_threads = [t for t in email_threads if t.slug == slug]

        if not email_threads:
            raise Http404()

        return Response(EmailThreadSerializer(email_threads, many=True).data)

    def create(self, request, *args, **kwargs):
        issue = self.get_object()
        data = {
            **request.data,
            "from_address": build_clerk_address(issue, email_only=True),
            "state": EmailState.DRAFT,
            "sender": request.user,
            "issue_id": issue.ok,
        }
        serializer = EmailSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)

    @action(
        detail=True,
        methods=["GET"],
        url_name="media-delete",
        url_path="delete_media/(?P<media_pk>[^/.]+)",
    )
    def retrieve_email(self, request, pk=None, media_pk=None):
        issue = self.get_object()
        return Response(serializer.data)

    # FIXME: IMPLEMENT PROPERLY
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        issue = self.get_object()
        # email = self.get_object()
        data = {**request.data}
        if email.state == EmailState.READY_TO_SEND:
            data["html"] = _render_email_template(email.html)

        serializer = self.get_serializer(email, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    # FIXME: IMPLEMENT PROPERLY
    def destroy(self, request, *args, **kwargs):
        email = self.get_object()
        with transaction.atomic():
            email.emailattachment_set.all().delete()
            email.delete()

        return Response(status=204)

    # FIXME: IMPLEMENT PROPERLY
    def create_attachment(self, request, *args, **kwargs):
        data = {
            **request.data,
            "sharepoint_state": SharepointState.UPLOADING,
        }
        serializer = EmailAttachmentSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)

    # FIXME: IMPLEMENT PROPERLY
    def delete_attachment(self, request, *args, **kwargs):
        pass

    # FIXME: IMPLEMENT PROPERLY
    def upload_attachment_to_sharepoint(self, request, *args, **kwargs):
        pass

    # FIXME: IMPLEMENT PROPERLY
    def download_attachment_from_sharepoint(self, request, *args, **kwargs):
        pass


def get_email_threads(issue: Issue) -> List[EmailThread]:
    email_qs = (
        issue.email_set.filter(state__in=DISPLAY_EMAIL_STATES)
        .prefetch_related("emailattachment_set")
        .order_by("created_at")
    )
    threads = []
    for email in email_qs:
        process_email_for_display(email)

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


def process_email_for_display(email: Email):
    email.html = get_email_html(email)
    for attachment in email.emailattachment_set.all():
        attachment.file.display_name = os.path.basename(attachment.file.name)


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
    return render_to_string("case/email_preview.html", context)


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


# @api_view(["GET", "POST"])
# @paralegal_or_better_required
# def email_draft_create_view(request, pk):
#     issue = _get_issue_for_emails(request, pk)
#     if request.method == "POST":
#         data = {
#             "from_address": build_clerk_address(issue, email_only=True),
#             "state": EmailState.DRAFT,
#             "sender": request.user,
#             **request.data,
#         }
#         serializer = EmailSerializer(data=data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save(issue=issue)
#         return Response(serializer.data)
#     else:
#         templates = EmailTemplate.objects.filter(
#             Q(topic=issue.topic) | Q(topic="GENERAL")
#         ).order_by("created_at")
#         parent_id = request.GET.get("parent")
#         parent_email = None
#         if parent_id:
#             try:
#                 parent_email = EmailSerializer(Email.objects.get(pk=parent_id)).data
#             except Email.DoesNotExist:
#                 raise Http404()

#         context = {
#             "case_email_url": reverse("case-email-list", args=(issue.pk,)),
#             "parent_email": parent_email,
#             "issue": IssueSerializer(issue).data,
#             "templates": EmailTemplateSerializer(templates, many=True).data,
#         }
#         return render_react_page(
#             request, f"Case {issue.fileref}", "email-draft-create", context
# )


# @api_view(["GET", "PATCH", "DELETE"])
# @paralegal_or_better_required
# def email_draft_edit_view(request, pk, email_pk):
#     issue = _get_issue_for_emails(request, pk)
#     email = _get_email_for_issue(issue, email_pk)
#     if not email.state in DRAFT_EMAIL_STATES:
#         return redirect("case-email-list", issue.pk)
#     if request.method == "PATCH":
#         serializer = EmailSerializer(email, data=request.data, partial=True)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)
#     elif request.method == "DELETE":
#         with transaction.atomic():
#             email.emailattachment_set.all().delete()
#             email.delete()
#         return Response({})
#     else:
#         # GET request.
#         api = MSGraphAPI()
#         sharepoint_docs = api.folder.get_all_files(f"cases/{issue.id}")
#         context = {
#             "email_preview_url": reverse(
#                 "case-email-preview", args=(issue.pk, email.pk)
#             ),
#             "case_email_url": reverse("case-email-list", args=(issue.pk,)),
#             "issue": IssueSerializer(issue).data,
#             "email": EmailSerializer(email).data,
#             "sharepoint_docs": sharepoint_docs,
#         }
#         return render_react_page(
#             request, f"Case {issue.fileref}", "email-draft-edit", context
#         )


# @api_view(["POST"])
# @paralegal_or_better_required
# def email_draft_send_view(request, pk, email_pk):
#     issue = _get_issue_for_emails(request, pk)
#     email = _get_email_for_issue(issue, email_pk)
#     if email.state == EmailState.DRAFT:
#         email.state = EmailState.READY_TO_SEND
#         email.html = _render_email_template(email.html)
#         email.save()
#     else:
#         raise Http404()

#     return Response(status=200)


# @api_view(["POST", "DELETE"])
# @paralegal_or_better_required
# def email_attachment_view(request, pk, email_pk, attach_pk=None):
#     """Delete the email attachment, return HTML fragment for htmx."""
#     issue = _get_issue_for_emails(request, pk)
#     email = _get_email_for_issue(issue, email_pk)
#     if not email.state == EmailState.DRAFT:
#         raise Http404()

#     if request.method == "DELETE":
#         email.emailattachment_set.filter(id=attach_pk).delete()
#         return Response(status=200)

#     else:
#         # POST request.
#         if "sharepoint_id" in request.data:
#             # Download attachment from SharePoint.
#             sharepoint_id = request.data["sharepoint_id"]
#             api = MSGraphAPI()
#             filename, content_type, file_bytes = api.folder.download_file(sharepoint_id)
#             # Save as email attachment
#             f = ContentFile(file_bytes, name=filename)
#         elif "file" in request.data:
#             f = request.data["file"]
#             content_type = f.content_type
#         else:
#             msg = "Could not find and uploaded file or SharePoint document."
#             raise ValidationError(msg)

#         if f.size / 1024 / 1024 > 30:
#             raise ValidationError({"file": "File must be <30MB."})

#         attach = EmailAttachment.objects.create(
#             email=email,
#             file=f,
#             content_type=content_type,
#         )
#         serializer = EmailAttachmentSerializer(attach)
#         return Response(serializer.data)


# @api_view(["POST"])
# @paralegal_or_better_required
# def email_attachment_upload_view(request, pk, email_pk, attach_pk):
#     """Save the attachment to Sharepoint"""
#     issue = _get_issue_for_emails(request, pk)
#     email = _get_email_for_issue(issue, email_pk)
#     try:
#         attachment = EmailAttachment.objects.get(pk=attach_pk)
#     except EmailAttachment.DoesNotExist:
#         raise Http404()

#     attachment.sharepoint_state = SharepointState.UPLOADING
#     attachment.save()
#     save_email_attachment(email, attachment)
#     attachment.sharepoint_state = SharepointState.UPLOADED
#     attachment.save()
#     return Response(data=EmailAttachmentSerializer(instance=attachment).data)


# def _get_email_for_issue(issue, email_pk):
#     try:
#         return issue.email_set.get(pk=email_pk)
#     except Email.DoesNotExist:
#         raise Http404()


# def _get_issue_for_emails(request, pk):
#     try:
#         return (
#             Issue.objects.check_permissions(request)
#             .prefetch_related("email_set__emailattachment_set")
#             .get(pk=pk)
#         )
#     except Issue.DoesNotExist:
#         raise Http404()
