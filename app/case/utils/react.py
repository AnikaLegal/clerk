import json

from django.shortcuts import render
from django.conf import settings
from django.urls import reverse


def render_react_page(request, title, react_page_name, react_context, public=False):

    react_context.update(
        {
            "user": {
                "id": request.user.id,
                "full_name": request.user.get_full_name(),
                "email": request.user.email,
                "url": reverse("account-detail", args=(request.user.pk,)),
                "is_admin": request.user.is_admin,
                "is_coordinator": request.user.is_coordinator,
                "is_lawyer": request.user.is_lawyer,
                "is_paralegal": request.user.is_paralegal,
                "is_admin_or_better": request.user.is_admin_or_better,
                "is_coordinator_or_better": request.user.is_coordinator_or_better,
                "is_lawyer_or_better": request.user.is_lawyer_or_better,
                "is_paralegal_or_better": request.user.is_paralegal_or_better,
            }
        }
    )
    context = {
        "SENTRY_JS_DSN": settings.SENTRY_JS_DSN,
        "react_context": json.dumps(react_context),
        "react_page_name": react_page_name,
        "title": title,
        "public": public,
    }
    return render(request, "case/react_base.html", context)
