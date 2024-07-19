from django.http import Http404
from django.urls import reverse
from rest_framework.decorators import api_view
from rest_framework.viewsets import ModelViewSet

from task.models import TaskTrigger
from task.serializers import TaskTemplateSerializer
from case.utils.react import render_react_page

from case.views.auth import (
    coordinator_or_better_required,
    CoordinatorOrBetterPermission,
)


@api_view(["GET"])
@coordinator_or_better_required
def template_task_list_page_view(request):
    context = {}
    return render_react_page(request, "Task Templates", "task-template-list", context)


@api_view(["GET"])
@coordinator_or_better_required
def template_task_create_page_view(request):
    context = {}
    return render_react_page(request, "Task Templates", "task-template-create", context)


@api_view(["GET"])
@coordinator_or_better_required
def template_task_detail_page_view(request, pk):
    try:
        trigger = TaskTrigger.objects.get(pk=pk)
    except TaskTrigger.DoesNotExist:
        raise Http404()

    context = {}
    return render_react_page(request, "Task Templates", "task-template-detail", context)


class TaskTemplateApiViewset(ModelViewSet):
    serializer_class = TaskTemplateSerializer
    permission_classes = [CoordinatorOrBetterPermission]

    def get_queryset(self):
        queryset = TaskTrigger.objects.order_by("-created_at").all()
        return queryset
