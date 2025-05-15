from core.models.document_template import DocumentTemplate
from core.models.issue import CaseTopic
from django.db.models import CharField, Value
from django.db.models.functions import Reverse, Right, StrIndex
from django.urls import reverse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from case.serializers import (
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

        # Annotate the queryset to extract the file name from the file path so
        # we can filter by name only.
        queryset = DocumentTemplate.objects.all()
        queryset = queryset.order_by("name")

        for key, value in serializer.validated_data.items():
            if value is not None:
                if key == "name":
                    queryset = queryset.filter(name__icontains=value)
                else:
                    queryset = queryset.filter(**{key: value})

        data = DocumentTemplateSerializer(queryset, many=True).data
        return Response(data=data)

    def create(self, request):
        serializer = DocumentTemplateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=201)

    def destroy(self, request, pk):
        template = DocumentTemplate.objects.get(pk=pk)
        template.delete()
        return Response(status=204)
