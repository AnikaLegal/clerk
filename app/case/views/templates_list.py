from django.urls import reverse
from rest_framework.decorators import api_view

from case.utils.react import render_react_page
from case.views.auth import coordinator_or_better_required


@api_view(["GET"])
@coordinator_or_better_required
def template_list_page_view(request):
    context = {
        "email_url": reverse("template-email-list"),
        "doc_url": reverse("template-doc-list"),
        "notify_url": reverse("template-notify-list"),
    }
    return render_react_page(request, "Templates", "template-list", context)
