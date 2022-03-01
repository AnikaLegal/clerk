from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.http import Http404
from django.contrib import messages
from django.db.models import Q

from emails.forms import EmailTemplateForm
from emails.models import EmailTemplate
from .auth import paralegal_or_better_required, coordinator_or_better_required
from case.utils.router import Router

router = Router("template")
router.create_route("list")
router.create_route("email-list").path("email")
router.create_route("email-detail").path("email").pk("pk")
router.create_route("email-create").path("email").path("create")
router.create_route("email-search").path("email").path("search")
router.create_route("doc-list").path("doc")
router.create_route("doc-detail").path("doc").pk("pk")
router.create_route("doc-create").path("doc").path("create")
router.create_route("doc-search").path("doc").path("search")


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
@paralegal_or_better_required
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
@paralegal_or_better_required
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
    context = {"templates": EmailTemplate.objects.order_by("-created_at").all()}
    return render(request, "case/templates/doc/list.html", context)


@router.use_route("doc-search")
@paralegal_or_better_required
@require_http_methods(["GET"])
def template_doc_search_view(request):
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
    return render(request, "case/templates/doc/_search.html", context)


@router.use_route("doc-detail")
@paralegal_or_better_required
@require_http_methods(["GET", "POST"])
def template_doc_detail_view(request, pk):
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
                return redirect("template-doc-detail", person.pk)
        else:
            form = EmailTemplateForm(instance=template)

        context = {"template": template, "form": form}
        return render(request, "case/templates/doc/edit.html", context)
    else:
        context = {"template": template}
        return render(request, "case/templates/doc/detail.html", context)


@router.use_route("doc-create")
@coordinator_or_better_required
@require_http_methods(["GET", "POST"])
def template_doc_create_view(request):
    if request.method == "POST":
        form = EmailTemplateForm(request.POST)
        if form.is_valid():
            template = form.save()
            messages.success(request, "Template created")
            return redirect("template-doc-detail", template.pk)
    else:
        form = EmailTemplateForm()

    context = {"form": form}
    return render(request, "case/templates/doc/create.html", context)
