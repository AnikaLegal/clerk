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
router.create_route("detail").pk("pk")
router.create_route("create").path("create")
router.create_route("search").path("search")


@router.use_route("list")
@coordinator_or_better_required
@require_http_methods(["GET"])
def template_list_view(request):
    context = {"templates": EmailTemplate.objects.order_by("-created_at").all()}
    return render(request, "case/templates/list.html", context)


@router.use_route("search")
@paralegal_or_better_required
@require_http_methods(["GET"])
def template_search_view(request):
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
    return render(request, "case/templates/_search.html", context)


@router.use_route("detail")
@paralegal_or_better_required
@require_http_methods(["GET", "POST"])
def template_detail_view(request, pk):
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
                return redirect("template-detail", person.pk)
        else:
            form = EmailTemplateForm(instance=template)

        context = {"template": template, "form": form}
        return render(request, "case/templates/edit.html", context)
    else:
        context = {"template": template}
        return render(request, "case/templates/detail.html", context)


@router.use_route("create")
@coordinator_or_better_required
@require_http_methods(["GET", "POST"])
def template_create_view(request):
    if request.method == "POST":
        form = EmailTemplateForm(request.POST)
        if form.is_valid():
            template = form.save()
            messages.success(request, "Template created")
            return redirect("template-detail", template.pk)
    else:
        form = EmailTemplateForm()

    context = {"form": form}
    return render(request, "case/templates/create.html", context)
