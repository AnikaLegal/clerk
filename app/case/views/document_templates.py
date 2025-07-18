from core.models.document_template import DocumentTemplate
from core.models.issue import CaseTopic
from django.shortcuts import get_object_or_404
from django.urls import reverse
from rest_framework import status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from case.serializers import (
    DocumentTemplateFilterSerializer,
    DocumentTemplateRenameSerializer,
    DocumentTemplateSerializer,
)
from case.utils.react import render_react_page
from case.views.auth import (
    AdminOrBetterPermission,
    admin_or_better_required,
)


@api_view(["GET"])
@admin_or_better_required
def template_doc_list_page_view(request):
    context = {
        "choices": {
            "topic": CaseTopic.ACTIVE_CHOICES,
        },
        "create_url": reverse("template-doc-create"),
    }
    return render_react_page(
        request, "Document Templates", "doc-template-list", context
    )


@api_view(["GET"])
@admin_or_better_required
def template_doc_create_page_view(request):
    context = {
        "choices": {
            "topic": CaseTopic.ACTIVE_CHOICES,
        },
        "list_url": reverse("template-doc-list"),
    }
    return render_react_page(
        request, "Document Templates", "doc-template-create", context
    )


class DocumentTemplateApiViewset(ViewSet):
    permission_classes = [AdminOrBetterPermission]

    def list(self, request):
        serializer = DocumentTemplateFilterSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        queryset = DocumentTemplate.objects.all()
        queryset = queryset.order_by("topic", "name")

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
        return Response(status=status.HTTP_201_CREATED)

    def destroy(self, request, pk):
        template = DocumentTemplate.objects.get(pk=pk)
        template.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["PATCH"],
        url_path="rename-file",
    )
    def rename_file(self, request, pk=None):
        serializer = DocumentTemplateRenameSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_name = serializer.validated_data.get("name")

        template = get_object_or_404(DocumentTemplate.objects, pk=pk)
        if new_name and template.name != new_name:
            field_file = template.file.open()
            field_file.file.name = new_name
            template.file.save(new_name, field_file.file)

        return Response(status=status.HTTP_204_NO_CONTENT)
