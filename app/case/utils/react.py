import json

from accounts.role import UserRole
from django.conf import settings
from django.shortcuts import render


def render_react_page(
    request, title, react_page_name, react_context, public=False, status=None
):
    react_context.update({"user": UserRole.flags_for(request.user)})
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
