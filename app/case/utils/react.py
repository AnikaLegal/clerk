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
    return render(request, "case/react_base.html", context)


def is_react_api_call(request):
    return bool(request.META.get("HTTP_X_REACT"))
