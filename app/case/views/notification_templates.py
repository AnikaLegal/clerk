from django.http import Http404
from django.urls import reverse
from rest_framework.decorators import api_view
from rest_framework.viewsets import ModelViewSet

from case.utils.react import render_react_page
from case.serializers import NotificationSerializer
from core.models.issue import CaseTopic
from notify.models import Notification

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
def template_notify_list_page_view(request):
    notifications = Notification.objects.order_by("-created_at").all()
    context = {
        "topic_options": topic_options,
        "create_url": reverse("template-notify-create"),
        "notifications": NotificationSerializer(notifications, many=True).data,
    }
    return render_react_page(
        request, "Notification Templates", "notify-template-list", context
    )


@api_view(["GET"])
@admin_or_better_required
def template_notify_create_page_view(request):
    return render_react_page(
        request,
        "Notification Templates",
        "notify-template-create",
        {
            "topic_options": topic_options,
        },
    )


@api_view(["GET"])
@admin_or_better_required
def template_notify_detail_page_view(request, pk):
    try:
        template = Notification.objects.get(pk=pk)
    except Notification.DoesNotExist:
        raise Http404()

    context = {
        "topic_options": topic_options,
        "template": NotificationSerializer(template).data,
        "notify_template_url": reverse("template-notify-list"),
    }
    return render_react_page(
        request, "Notification Templates", "notify-template-detail", context
    )


class NotifyTemplateApiViewset(ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [AdminOrBetterPermission]

    def get_queryset(self):
        """Filter by query params"""
        queryset = Notification.objects.order_by("-created_at").all()
        name = self.request.query_params.get("name")
        topic = self.request.query_params.get("topic")

        if name:
            queryset = queryset.filter(name__icontains=name)

        if topic:
            queryset = queryset.filter(topic=topic)

        return queryset
