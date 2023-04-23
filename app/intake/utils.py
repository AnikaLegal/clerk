import json

from django.shortcuts import render
from django.conf import settings


def render_react_page(request, title, react_page_name, react_context, public=False):
    context = {
        "SENTRY_JS_DSN": settings.SENTRY_JS_DSN,
        "react_context": json.dumps(react_context),
        "react_page_name": react_page_name,
        "title": title,
        "public": public,
    }
    return render(request, "intake/react_base.html", context)
