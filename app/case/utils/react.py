import json

from django.shortcuts import render


def render_react_page(request, title, react_page_name, react_context):
    context = {
        "react_context": json.dumps(react_context),
        "react_page_name": react_page_name,
        "title": title,
    }
    return render(request, "case/react_base.html", context)


def is_react_api_call(request):
    return bool(request.META.get("HTTP_X_REACT"))
