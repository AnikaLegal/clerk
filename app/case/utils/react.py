import json
import logging

import requests
from django.shortcuts import render
from django.conf import settings

logger = logging.getLogger(__name__)


def render_react_page(request, title, react_page_name, react_context):
    react_html = ""
    try:
        resp = requests.post(
            f"http://ssr:3002/render/{react_page_name}/",
            json=react_context,
            timeout=0.1,
        )
        react_html = resp.text
    except (requests.HTTPError, requests.ReadTimeout, requests.ConnectionError):
        logger.exception("Server side rendering failed")

    context = {
        "react_html": react_html,
        "SENTRY_JS_DSN": settings.SENTRY_JS_DSN,
        "react_context": json.dumps(react_context),
        "react_page_name": react_page_name,
        "title": title,
    }
    return render(request, "case/react_base.html", context)


def is_react_api_call(request):
    return bool(request.META.get("HTTP_X_REACT"))
