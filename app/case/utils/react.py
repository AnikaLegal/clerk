import json

from django.shortcuts import render


def render_react_page(request, title, react_page_name, react_context):
    context = {
        "react_context": json.dumps(react_context),
        "react_page_name": react_page_name,
        "title": title,
    }
    return render(request, "case/react_base.html", context)
