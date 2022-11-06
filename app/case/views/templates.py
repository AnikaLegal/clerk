from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.http import Http404, HttpResponse
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from case.utils.router import Router
from case.forms import DocumentTemplateForm
from case.utils.react import render_react_page
from case.serializers import EmailTemplateSerializer, NotificationSerializer
from emails.models import EmailTemplate
from core.models.issue import CaseTopic
from notify.models import Notification
from microsoft.service import list_templates, upload_template, delete_template

from .auth import coordinator_or_better_required, paralegal_or_better_required

router = Router("template")
router.create_route("list")

# Emails
router.create_route("email-list").path("email")
router.create_route("email-detail").path("email").pk("pk")
router.create_route("email-create").path("email").path("create")
router.create_route("email-search").path("email").path("search")

# Documents
router.create_route("doc-list").path("doc")
router.create_route("doc-create").path("doc").path("create")
router.create_route("doc-search").path("doc").path("search")
router.create_route("doc-delete").path("doc").slug("file_id").path("delete")

# Notifications
router.create_route("notify-list").path("notify")
router.create_route("notify-create").path("notify").path("create")
router.create_route("notify-search").path("notify").path("search")
router.create_route("notify-detail").path("notify").pk("pk")
router.create_route("notify-delete").path("notify").pk("pk").path("delete")


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
    context = {
        "topic": CaseTopic.REPAIRS,
        "create_url": reverse("template-doc-create"),
    }
    return render_react_page(
        request, "Document Templates", "doc-template-list", context
    )


@router.use_route("doc-search")
@coordinator_or_better_required
@api_view(["GET"])
def template_doc_search_view(request):
    topic = request.GET.get("topic", CaseTopic.REPAIRS)
    templates = [{**t, "topic": topic} for t in list_templates(topic)]
    name = request.GET.get("name")
    if name:
        templates = [t for t in templates if name.lower() in t["name"].lower()]

    templates = sorted(templates, key=lambda t: t["name"])
    return Response(data=templates)


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


@router.use_route("notify-list")
@coordinator_or_better_required
@api_view(["GET"])
def template_notify_list_view(request):
    notifications = Notification.objects.order_by("-created_at").all()
    context = {
        "create_url": reverse("template-notify-create"),
        "notifications": NotificationSerializer(notifications, many=True).data,
    }
    return render_react_page(
        request, "Notification Templates", "notify-template-list", context
    )


@router.use_route("notify-search")
@coordinator_or_better_required
@api_view(["GET"])
def template_notify_search_view(request):
    notifications = Notification.objects.order_by("-created_at").all()
    name = request.GET.get("name")
    if name:
        notifications = notifications.filter(name__icontains=name)

    topic = request.GET.get("topic")
    if topic:
        notifications = notifications.filter(topic=topic)

    return Response(NotificationSerializer(notifications, many=True).data)


@router.use_route("notify-delete")
@coordinator_or_better_required
@api_view(["DELETE"])
def template_notify_delete_view(request, pk):
    try:
        template = Notification.objects.get(pk=pk)
    except Notification.DoesNotExist:
        raise Http404()

    template.delete()
    return Response({})


@router.use_route("notify-create")
@coordinator_or_better_required
@api_view(["GET", "POST"])
def template_notify_create_view(request):
    if request.method == "POST":
        serializer = NotificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return render_react_page(
        request, "Notification Templates", "notify-template-create", {}
    )


@router.use_route("notify-detail")
@coordinator_or_better_required
@api_view(["GET", "PUT"])
def template_notify_detail_view(request, pk):
    try:
        template = Notification.objects.get(pk=pk)
    except Notification.DoesNotExist:
        raise Http404()

    if request.method == "PUT":
        serializer = NotificationSerializer(instance=template, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    context = {
        "template": NotificationSerializer(template).data,
        "notify_template_url": reverse("template-notify-list"),
    }
    return render_react_page(
        request, "Notification Templates", "notify-template-edit", context
    )
