import re

import bleach
from django.http import Http404
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.utils.html import strip_tags

from core.models import Issue
from case.views.auth import paralegal_or_better_required
from emails.service import build_clerk_address


@paralegal_or_better_required
@require_http_methods(["GET", "POST"])
def case_detail_email_view(request, pk, form_slug=""):
    try:
        issue = (
            Issue.objects.check_permisisons(request)
            .prefetch_related("email_set")
            .get(pk=pk)
        )
    except Issue.DoesNotExist:
        raise Http404()

    if form_slug == "draft":
        pass
    elif form_slug == "email":
        pass

    case_email_address = build_clerk_address(issue)
    emails = (
        issue.email_set.prefetch_related("emailattachment_set")
        .order_by("-created_at")
        .all()
    )
    for email in emails:
        email.html = get_email_html(email)

    context = {
        "issue": issue,
        "emails": emails,
        "case_email_address": case_email_address,
    }
    return render(request, "case/case_detail_email.html", context)


ALLOWED_TAGS = [
    "p",
    "a",
    "br",
    "b",
    "i",
    "strong",
    "em",
    "img",
    "div",
    "span",
    "ul",
    "li",
    "blockquote",
    "ol",
]
ALLOWED_ATTRS = ["style"]


def get_email_html(email) -> str:
    if email.html:
        # Sanitize HTML to prevent script injection attacks.
        return bleach.clean(email.html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS)
    else:
        text = email.text.replace("\r", "")
        text = re.sub("\n(?!\n)", " <br/>", text)
        return "".join(
            [f"<p>{line}</p>" for line in strip_tags(text).split("\n") if line]
        )
