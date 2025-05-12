import os

from core.models.issue import CaseTopic
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from django.utils.text import slugify
from microsoft.service import delete_file, list_path
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from case.serializers import (
    DocumentTemplateFileSerializer,
    DocumentTemplateFilterSerializer,
    DocumentTemplateSerializer,
)
from case.utils.react import render_react_page
from case.views.auth import (
    CoordinatorOrBetterPermission,
    coordinator_or_better_required,
)

topic_options = [
    {"key": key, "value": key, "text": label} for key, label in CaseTopic.ACTIVE_CHOICES
]


@api_view(["GET"])
@coordinator_or_better_required
def template_doc_list_page_view(request):
    context = {
        "topic_options": topic_options,
        "topic": CaseTopic.REPAIRS,
        "create_url": reverse("template-doc-create"),
    }
    return render_react_page(
        request, "Document Templates", "doc-template-list", context
    )


@api_view(["GET"])
@coordinator_or_better_required
def template_doc_create_page_view(request):
    context = {"topic_options": topic_options, "list_url": reverse("template-doc-list")}
    return render_react_page(
        request, "Document Templates", "doc-template-create", context
    )


class DocumentTemplateApiViewset(ViewSet):
    permission_classes = [CoordinatorOrBetterPermission]

    def list(self, request):
        serializer = DocumentTemplateFilterSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        query_params = serializer.validated_data

        topic = query_params.get("topic", CaseTopic.REPAIRS)
        subtopic = query_params.get("subtopic", "")
        name = query_params.get("name")

        path = os.path.join("templates", slugify(topic), slugify(subtopic)).rstrip("/")
        serializer = DocumentTemplateSerializer(list_path(path), many=True)

        templates = []
        for item in serializer.data:
            if name and name.lower() not in item["name"].lower():
                continue

            item["topic"] = topic
            if subtopic:
                item["subtopic"] = subtopic
            templates.append(item)

        templates = sorted(templates, key=lambda x: x["name"])
        return Response(data=templates)

    def create(self, request):
        serializer = DocumentTemplateFileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=201)

    def destroy(self, request, pk):
        try:
            delete_file(file_id=pk, allowed_path="/drive/root:/templates")
        except PermissionError:
            raise PermissionDenied
        return Response(status=204)
