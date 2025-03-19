import os
from typing import List
from io import BytesIO

from django.http import Http404, HttpResponse
from django.urls import reverse
from django.db.models import Q
from django.db import transaction
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from emails.utils.threads import EmailThread
from emails.utils.html import parse_email_html, render_email_template
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


@api_view(["GET"])
@paralegal_or_better_required
def email_list_page_view(request, pk):
    viewset = get_viewset(request=request, pk=pk)
    issue = viewset.get_object()
    case_email_address = build_clerk_address(issue)
    context = {
        "case_pk": pk,
        "urls": get_detail_urls(issue),
        "case_email_address": case_email_address,
        "draft_url": reverse("case-email-draft", args=(issue.pk,)),
    }
    return render_react_page(request, f"Case {issue.fileref}", "email-list", context)


@api_view(["GET"])
@paralegal_or_better_required
def email_thread_page_view(request, pk, slug):
    viewset = get_viewset(request=request, pk=pk)
    issue = viewset.get_object()
    context = {
        "case_pk": pk,
        "thread_slug": slug,
        "case_email_list_url": reverse("case-email-list", args=(issue.pk,)),
    }
    return render_react_page(request, f"Case {issue.fileref}", "email-thread", context)


@api_view(["GET"])
@paralegal_or_better_required
def email_draft_create_page_view(request, pk):
    viewset = get_viewset(request=request, pk=pk)
    issue = viewset.get_object()
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
    viewset = get_viewset(request=request, pk=pk)
    issue = viewset.get_object()
    context = {
        "case_pk": pk,
        "email_pk": email_pk,
        "email_preview_url": reverse("case-email-preview", args=(issue.pk, email_pk)),
        "case_email_url": reverse("case-email-list", args=(issue.pk,)),
    }
    return render_react_page(
        request, f"Case {issue.fileref}", "email-draft-edit", context
    )


@api_view(["GET"])
@paralegal_or_better_required
def email_draft_preview_page_view(request, pk, email_pk):
    viewset = get_viewset(request=request, pk=pk)
    email = viewset.get_email(email_pk=email_pk)
    html = render_email_template(email.html)
    return HttpResponse(html, "text/html", 200)


def get_viewset(request, **kwargs):
    viewset = EmailApiViewset(request=request, **kwargs)
    viewset.setup(request, **kwargs)
    return viewset


class EmailApiViewset(GenericViewSet):
    serializer_class = EmailThreadSerializer
    permission_classes = [
        CoordinatorOrBetterPermission | ParalegalOrBetterObjectPermission
    ]

    def get_queryset(self):
        user = self.request.user
        queryset = Issue.objects.prefetch_related("email_set__emailattachment_set")
        if user.is_paralegal:
            # Paralegals can only see assigned cases
            queryset = queryset.filter(paralegal=user)
        elif user.is_lawyer:
            # Lawyers can only see assigned cases
            queryset = queryset.filter(lawyer=user)
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

    @action(detail=True, methods=["POST"], url_name="create", url_path="create")
    def create_email(self, request, *args, **kwargs):
        issue = self.get_object()
        data = {
            **request.data,
            "from_address": build_clerk_address(issue, email_only=True),
            "state": EmailState.DRAFT,
            "issue": issue.pk,
        }
        serializer = EmailSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        email = serializer.save()
        email.sender = request.user
        email.save()
        return Response(EmailSerializer(email).data, status=201)

    def get_email(self, email_pk: int) -> Email:
        issue = self.get_object()
        try:
            email = issue.email_set.prefetch_related("emailattachment_set").get(
                pk=email_pk
            )
        except Email.DoesNotExist:
            raise Http404()

        return email

    @action(
        detail=True,
        methods=["GET"],
        url_name="email-detail",
        url_path=r"(?P<email_id>[0-9]+)",
    )
    def email_detail(self, request, pk=None, email_id=None):
        email = self.get_email(email_id)
        return Response(EmailSerializer(email).data)

    @email_detail.mapping.patch
    def update(self, request, pk=None, email_id=None, **kwargs):
        email = self.get_email(email_id)
        if not email.state == EmailState.DRAFT:
            raise Http404()

        data = {**request.data}
        if data.get("state") == EmailState.READY_TO_SEND:
            data["html"] = render_email_template(data["html"])

        serializer = EmailSerializer(email, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @email_detail.mapping.delete
    def destroy(self, request, pk=None, email_id=None):
        email = self.get_email(email_id)
        if not email.state == EmailState.DRAFT:
            raise Http404()

        with transaction.atomic():
            email.emailattachment_set.all().delete()
            email.delete()

        return Response(status=204)

    @action(
        detail=True,
        methods=["POST"],
        url_name="attachment-create",
        url_path=r"(?P<email_id>[0-9]+)/attachment",
    )
    def create_attachment(self, request, pk=None, email_id=None):
        email = self.get_email(email_id)
        if not email.state == EmailState.DRAFT:
            raise Http404()

        request.data["email"] = email_id
        serializer = EmailAttachmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)

    def get_attachment(self, email: Email, attachment_id: int) -> EmailAttachment:
        try:
            attachment = email.emailattachment_set.get(pk=attachment_id)
        except EmailAttachment.DoesNotExist:
            raise Http404()

        return attachment

    @action(
        detail=True,
        methods=["DELETE"],
        url_name="attachment-delete",
        url_path=r"(?P<email_id>[0-9]+)/attachment/(?P<attachment_id>[0-9]+)",
    )
    def delete_attachment(self, request, pk=None, email_id=None, attachment_id=None):
        email = self.get_email(email_id)
        if not email.state == EmailState.DRAFT:
            raise Http404()

        attachment = self.get_attachment(email, attachment_id)
        attachment.delete()
        return Response(status=204)

    @action(
        detail=True,
        methods=["POST"],
        url_name="attachment-sharepoint-upload",
        url_path=r"(?P<email_id>[0-9]+)/attachment/(?P<attachment_id>[0-9]+)/sharepoint",
    )
    def upload_attachment_to_sharepoint(
        self, request, pk=None, email_id=None, attachment_id=None
    ):
        """Save the attachment to Sharepoint"""
        email = self.get_email(email_id)
        attachment = self.get_attachment(email, attachment_id)
        attachment.sharepoint_state = SharepointState.UPLOADING
        attachment.save()
        save_email_attachment(email, attachment)
        attachment.sharepoint_state = SharepointState.UPLOADED
        attachment.save()
        return Response(status=204)

    @action(
        detail=True,
        methods=["POST"],
        url_name="attachment-sharepoint-download",
        url_path=r"(?P<email_id>[0-9]+)/attachment/sharepoint/(?P<sharepoint_id>[\-\w]+)",
    )
    def download_attachment_from_sharepoint(
        self, request, pk=None, email_id=None, sharepoint_id=None
    ):
        """Add a file from sharepoint as an attachment to an email"""
        email = self.get_email(email_id)
        if not email.state == EmailState.DRAFT:
            raise Http404()

        # Download attachment from SharePoint.
        api = MSGraphAPI()
        filename, content_type, file_bytes = api.folder.download_file(sharepoint_id)

        # Save as email attachment
        f = InMemoryUploadedFile(
            BytesIO(file_bytes),
            name=filename,
            content_type=content_type,
            field_name="file",
            size=len(file_bytes),
            charset=None,
        )
        data = {"file": f, "email": email_id}
        serializer = EmailAttachmentSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=204)


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
    email.html = parse_email_html(email)
    for attachment in email.emailattachment_set.all():
        attachment.file.display_name = os.path.basename(attachment.file.name)
