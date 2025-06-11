from django.http import Http404
from django.db.models import Q
from django.urls import reverse
from rest_framework.decorators import api_view
from rest_framework.viewsets import ModelViewSet

from case.utils.react import render_react_page
from case.serializers import EmailTemplateSerializer
from emails.models import EmailTemplate
from core.models.issue import CaseTopic

from case.views.auth import (
    admin_or_better_required,
    AdminOrBetterPermission,
)

topic_options = [
    {"key": "GENERAL", "value": "GENERAL", "text": "General"},
] + [
    {"key": key, "value": key, "text": label} for key, label in CaseTopic.ACTIVE_CHOICES
]


@api_view(["GET"])
@admin_or_better_required
def template_email_list_page_view(request):
    templates = EmailTemplate.objects.order_by("-created_at").all()
    context = {
        "topic_options": topic_options,
        "templates": EmailTemplateSerializer(templates, many=True).data,
        "create_url": reverse("template-email-create"),
    }
    return render_react_page(request, "Email Templates", "email-template-list", context)


@api_view(["GET"])
@admin_or_better_required
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
@admin_or_better_required
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
    permission_classes = [AdminOrBetterPermission]

    def get_queryset(self):
        """Filter by query params"""
        queryset = EmailTemplate.objects.order_by("-created_at").all()
        name = self.request.query_params.get("name")
        topic = self.request.query_params.get("topic")

        if name:
            queryset = queryset.filter(
                Q(name__icontains=name) | Q(subject__icontains=name)
            )

        if topic:
            queryset = queryset.filter(topic=topic)

        return queryset
