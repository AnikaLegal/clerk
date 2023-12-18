from django.urls import reverse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.viewsets import ViewSet
from django.core.exceptions import PermissionDenied

from case.utils.react import render_react_page
from core.models.issue import CaseTopic
from microsoft.service import list_templates, upload_template, delete_template
from case.serializers import DocumentTemplateSerializer
from case.views.auth import coordinator_or_better_required


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
    def list(self, request):
        if not request.user.is_coordinator_or_better:
            raise PermissionDenied

        topic = request.query_params.get("topic", CaseTopic.REPAIRS)
        name = request.query_params.get("name")
        templates = [{**t, "topic": topic} for t in list_templates(topic)]
        if name:
            templates = [t for t in templates if name.lower() in t["name"].lower()]

        templates = sorted(templates, key=lambda t: t["name"])
        return Response(data=templates)

    def create(self, request):
        """
        Note: requires muiltipart upload.
        """
        if not request.user.is_coordinator_or_better:
            raise PermissionDenied

        serializer = DocumentTemplateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        files = serializer.validated_data["files"]
        topic = serializer.validated_data["topic"]
        for f in files:
            upload_template(topic, f)

        return Response(status=201)

    def destroy(self, request, pk=None):
        if not request.user.is_coordinator_or_better:
            raise PermissionDenied

        if pk is not None:
            delete_template(file_id=pk)

        return Response(status=204)
