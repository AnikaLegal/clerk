from core.models.issue import CaseTopic
from django.db.models import Q
from django.http import Http404
from django.urls import reverse
from emails.models import EmailTemplate
from rest_framework.decorators import api_view
from rest_framework.viewsets import ModelViewSet

from case.serializers import EmailTemplateSerializer
from case.utils.react import render_react_page
from case.views.auth import (
    CoordinatorOrBetterCanWritePermission,
    coordinator_or_better_required,
    paralegal_or_better_required,
)

topic_options = [
    {"key": "GENERAL", "value": "GENERAL", "text": "General"},
] + [
    {"key": key, "value": key, "text": label} for key, label in CaseTopic.ACTIVE_CHOICES
]
TOPIC_CHOICES = CaseTopic.ACTIVE_CHOICES + [("GENERAL", "General")]


@api_view(["GET"])
@coordinator_or_better_required
def template_email_list_page_view(request):
    context = {
        "choices": {
            "topic": TOPIC_CHOICES,
        },
        "create_url": reverse("template-email-create"),
    }
    return render_react_page(request, "Email Templates", "email-template-list", context)


@api_view(["GET"])
@coordinator_or_better_required
def template_email_create_page_view(request):
    return render_react_page(
        request,
        "Create New Email Template",
        "email-template-create",
        {
            "topic_options": topic_options,
        },
    )


@api_view(["GET"])
@paralegal_or_better_required
def template_email_detail_page_view(request, pk):
    try:
        template = EmailTemplate.objects.get(pk=pk)
    except EmailTemplate.DoesNotExist:
        raise Http404()

    context = {
        "topic_options": topic_options,
        "template_list_url": reverse("template-email-list"),
        "template": EmailTemplateSerializer(template).data,
        "editable": request.user.is_coordinator_or_better,
    }
    return render_react_page(
        request, "Email Template", "email-template-detail", context
    )


class EmailTemplateApiViewset(ModelViewSet):
    serializer_class = EmailTemplateSerializer
    permission_classes = [CoordinatorOrBetterCanWritePermission]

    def get_queryset(self):
        """Filter by query params"""

        queryset = EmailTemplate.objects.order_by("topic", "name").all()
        name = self.request.query_params.get("name")
        topic = self.request.query_params.get("topic")

        if name:
            queryset = queryset.filter(
                Q(name__icontains=name) | Q(subject__icontains=name)
            )

        if topic:
            queryset = queryset.filter(topic=topic)

        return queryset
