import json

from django.conf import settings
from django.shortcuts import render


def render_intake_page(request, title, react_context=None):
    """
    Render the public intake single page app.

    Deliberately not case.utils.react.render_react_page: that helper injects
    staff permission context and dereferences request.user attributes that
    do not exist for AnonymousUser.
    """
    sentry_context = {
        "dsn": settings.SENTRY_JS_DSN or "",
        "environment": settings.ENVIRONMENT or "",
    }
    context = {
        "title": title,
        "react_context": json.dumps(react_context or {}),
        "sentry_context": json.dumps(sentry_context),
        # The shared navbar hides its "Get free help" call to action here: the
        # visitor is already in the intake form, so the link is redundant.
        "hide_intake_cta": True,
    }
    return render(request, "intake/base.html", context)
