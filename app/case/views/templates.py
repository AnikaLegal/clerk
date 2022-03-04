from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.http import Http404, HttpResponse
from django.contrib import messages
from django.db.models import Q

from emails.forms import EmailTemplateForm
from emails.models import EmailTemplate
from case.utils.router import Router
from core.models.issue import CaseTopic
from case.forms import DocumentTemplateForm
from microsoft.service import list_templates, upload_template, delete_template

from .auth import coordinator_or_better_required

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
    context = {"templates": EmailTemplate.objects.order_by("-created_at").all()}
    return render(request, "case/templates/list.html", context)


@router.use_route("email-list")
@coordinator_or_better_required
@require_http_methods(["GET"])
def template_email_list_view(request):
    context = {"templates": EmailTemplate.objects.order_by("-created_at").all()}
    return render(request, "case/templates/email/list.html", context)


@router.use_route("email-search")
@coordinator_or_better_required
@require_http_methods(["GET"])
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

    context = {"templates": templates}
    return render(request, "case/templates/email/_search.html", context)


@router.use_route("email-detail")
@coordinator_or_better_required
@require_http_methods(["GET", "POST"])
def template_email_detail_view(request, pk):
    try:
        template = EmailTemplate.objects.get(pk=pk)
    except EmailTemplate.DoesNotExist:
        raise Http404()

    if request.user.is_coordinator_or_better:
        if request.method == "POST":
            form = EmailTemplateForm(request.POST, instance=template)
            if form.is_valid():
                person = form.save()
                messages.success(request, "Edit successful")
                return redirect("template-email-detail", person.pk)
        else:
            form = EmailTemplateForm(instance=template)

        context = {"template": template, "form": form}
        return render(request, "case/templates/email/edit.html", context)
    else:
        context = {"template": template}
        return render(request, "case/templates/email/detail.html", context)


@router.use_route("email-create")
@coordinator_or_better_required
@require_http_methods(["GET", "POST"])
def template_email_create_view(request):
    if request.method == "POST":
        form = EmailTemplateForm(request.POST)
        if form.is_valid():
            template = form.save()
            messages.success(request, "Template created")
            return redirect("template-email-detail", template.pk)
    else:
        form = EmailTemplateForm()

    context = {"form": form}
    return render(request, "case/templates/email/create.html", context)


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
