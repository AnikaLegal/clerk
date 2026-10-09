import json

from accounts.role import ROLE_FLAGS
from django.conf import settings
from django.shortcuts import render


def render_react_page(
    request, title, react_page_name, react_context, public=False, status=None
):
    # Role flags are only annotated on authenticated users, but the 403/404
    # handlers also render this page for anonymous visitors.
    react_context.update(
        {"user": {flag: getattr(request.user, flag, False) for flag in ROLE_FLAGS}}
    )
    sentry_context = {
        "dsn": settings.SENTRY_JS_DSN or "",
        "environment": settings.ENVIRONMENT or "",
    }
    context = {
        "sentry_context": json.dumps(sentry_context),
        "react_context": json.dumps(react_context),
        "react_page_name": react_page_name,
        "title": title,
        "public": public,
    }
    return render(
        request=request,
        template_name="case/react_base.html",
        context=context,
        status=status,
    )
