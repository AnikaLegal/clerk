from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.http import Http404, HttpResponse
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from emails.forms import EmailTemplateForm
from emails.models import EmailTemplate
from case.utils.router import Router
from core.models.issue import CaseTopic
from case.forms import DocumentTemplateForm
from microsoft.service import list_templates, upload_template, delete_template
from case.utils.react import render_react_page
from case.serializers import EmailTemplateSerializer

from .auth import coordinator_or_better_required, paralegal_or_better_required

router = Router("template")
router.create_route("list")
router.create_route("email-list").path("email")
router.create_route("email-detail").path("email").pk("pk")
router.create_route("email-create").path("email").path("create")
router.create_route("email-search").path("email").path("search")
router.create_route("doc-list").path("doc")
router.create_route("doc-create").path("doc").path("create")
router.create_route("doc-search").path("doc").path("search")
router.create_route("doc-delete").path("doc").slug("file_id").path("delete")


@router.use_route("list")
@coordinator_or_better_required
@require_http_methods(["GET"])
def template_list_view(request):
    return render(request, "case/templates/list.html")


@router.use_route("email-list")
@coordinator_or_better_required
@require_http_methods(["GET"])
def template_email_list_view(request):
    templates = EmailTemplate.objects.order_by("-created_at").all()
    context = {
        "templates": EmailTemplateSerializer(templates, many=True).data,
        "create_url": reverse("template-email-create"),
    }
    return render_react_page(request, "Email Templates", "email-template-list", context)


@router.use_route("email-search")
@coordinator_or_better_required
@api_view(["GET"])
def template_email_search_view(request):
    templates = EmailTemplate.objects.order_by("-created_at").all()
    name = request.GET.get("name")
    if name:
        templates = templates.filter(
            Q(name__icontains=name) | Q(subject__icontains=name)
        )

    topic = request.GET.get("topic")
    if topic:
        templates = templates.filter(topic=topic)

    return Response(data=EmailTemplateSerializer(templates, many=True).data)


@router.use_route("email-create")
@coordinator_or_better_required
@api_view(["GET", "POST"])
def template_email_create_view(request):
    if request.method == "POST":
        serializer = EmailTemplateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return render_react_page(request, "Email Templates", "email-template-create", {})


@router.use_route("email-detail")
@paralegal_or_better_required
@api_view(["GET", "PUT"])
def template_email_detail_view(request, pk):
    try:
        template = EmailTemplate.objects.get(pk=pk)
    except EmailTemplate.DoesNotExist:
        raise Http404()

    if request.method == "PUT":
        if request.user.is_coordinator_or_better:
            serializer = EmailTemplateSerializer(instance=template, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            raise Http404()

    context = {
        "template": EmailTemplateSerializer(template).data,
        "editable": request.user.is_coordinator_or_better,
    }
    return render_react_page(
        request, "Email Templates", "email-template-detail", context
    )


@router.use_route("doc-list")
@coordinator_or_better_required
@require_http_methods(["GET"])
def template_doc_list_view(request):
    topic = request.GET.get("topic", CaseTopic.REPAIRS)
    context = {"templates": list_templates(topic), "topic": topic}
    return render(request, "case/templates/doc/list.html", context)


@router.use_route("doc-search")
@coordinator_or_better_required
@require_http_methods(["GET", "DELETE"])
def template_doc_search_view(request):
    topic = request.GET.get("topic", CaseTopic.REPAIRS)
    templates = list_templates(topic)
    name = request.GET.get("name")
    if name:
        templates = [t for t in templates if name.lower() in t["name"].lower()]

    templates = sorted(templates, key=lambda t: t["name"])
    context = {"templates": templates, "topic": topic}
    return render(request, "case/templates/doc/_search.html", context)


@router.use_route("doc-delete")
@coordinator_or_better_required
@require_http_methods(["DELETE"])
def template_doc_delete_view(request, file_id):
    delete_template(file_id)
    return HttpResponse()


@router.use_route("doc-create")
@coordinator_or_better_required
@require_http_methods(["GET", "POST"])
def template_doc_create_view(request):
    if request.method == "POST":
        form = DocumentTemplateForm(request.POST, files=request.FILES)
        if form.is_valid():
            files = request.FILES.getlist("files")
            for f in files:
                upload_template(form.cleaned_data["topic"], f)

            messages.success(request, "Templates uploaded")
            return redirect("template-doc-list")
    else:
        form = DocumentTemplateForm()

    context = {"form": form}
    return render(request, "case/templates/doc/create.html", context)
