from django.http import Http404
from django.urls import reverse
from rest_framework.decorators import api_view
from rest_framework.viewsets import ModelViewSet

from task.models.trigger import TaskTrigger, TriggerTopic, TasksCaseRole
from task.models.template import TaskType
from core.models.issue_event import EventType
from core.models.issue import CaseStage
from task.serializers import TaskTriggerSerializer
from case.utils.react import render_react_page

from case.views.auth import (
    coordinator_or_better_required,
    CoordinatorOrBetterPermission,
)


@api_view(["GET"])
@coordinator_or_better_required
def template_task_list_page_view(request):
    context = {
        "create_url": reverse("template-task-create"),
        "choices": {
            "topic": TriggerTopic.choices,
            "event": EventType.choices,
            "event_stage": CaseStage.CHOICES,
            "tasks_assignment_role": TasksCaseRole.choices,
        },
    }
    return render_react_page(request, "Task Templates", "task-template-list", context)


@api_view(["GET"])
@coordinator_or_better_required
def template_task_create_page_view(request):
    context = {
        "choices": {
            "topic": TriggerTopic.choices,
            "event": EventType.choices,
            "event_stage": CaseStage.CHOICES,
            "tasks_assignment_role": TasksCaseRole.choices,
            "task_type": TaskType.choices,
        },
    }
    return render_react_page(request, "Task Templates", "task-template-create", context)


@api_view(["GET"])
@coordinator_or_better_required
def template_task_detail_page_view(request, pk):
    try:
        trigger = TaskTrigger.objects.get(pk=pk)
    except TaskTrigger.DoesNotExist:
        raise Http404()

    context = {
        "list_url": reverse("template-task-list"),
    }
    return render_react_page(request, "Task Templates", "task-template-detail", context)


class TaskTemplateApiViewset(ModelViewSet):
    serializer_class = TaskTriggerSerializer
    permission_classes = [CoordinatorOrBetterPermission]

    def get_queryset(self):
        queryset = TaskTrigger.objects.order_by("-created_at").all()
        return queryset
