import crawleruseragents
from django.shortcuts import redirect, render
from django.templatetags.static import static
from django.utils.html import format_html
from wagtail import hooks
from wagtail.admin.ui.tables import BooleanColumn, LiveStatusTagColumn, UpdatedAtColumn
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

from .forms import DocumentLogForm
from .models import Banner, DashboardItem, DocumentLog, ExternalNews, Report


def global_admin_css():
    return format_html(
        '<link rel="stylesheet" href="{}">', static("web/styles/wagtail-admin.css")
    )


hooks.register("insert_global_admin_css", global_admin_css)


def before_serve_document(document, request):
    if request.user.is_authenticated or not getattr(document, "track_download", False):
        return None

    # Allow bots to access documents without logging a download.
    user_agent = request.META.get("HTTP_USER_AGENT", "")
    if crawleruseragents.is_crawler(user_agent):
        return None

    # Check cookie from request to see if the user has already logged a
    # response.
    file_hash = document.get_file_hash()
    cookie_name = f"document_logged_{file_hash}"
    if request.COOKIES.get(cookie_name) is not None:
        return None

    if request.method == "POST":
        form = DocumentLogForm(request.POST)
        if form.is_valid():
            ip_address = request.META.get("REMOTE_ADDR")
            DocumentLog.objects.create(
                document=document,
                ip_address=ip_address,
                state=form.cleaned_data["state"],
                referrer=form.cleaned_data["referrer"],
                sector=form.cleaned_data["sector"],
            )
            response = redirect(document.url)
            response.set_cookie(
                cookie_name,
                "true",
                max_age=60 * 60 * 24 * 365,  # 1 year
                secure=True,
                httponly=True,
                samesite="Strict",
            )
            return response
    else:
        form = DocumentLogForm()

    context = {
        "form": form,
        "document": document,
    }
    return render(request, "web/_download.html", context)


hooks.register("before_serve_document", before_serve_document)


class BannerAdmin(SnippetViewSet):
    model = Banner
    menu_label = "Banner"
    icon = "minus"
    menu_order = 200
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_display = ("title", "is_active")
    search_fields = ("title",)


register_snippet(BannerAdmin)


class DashboardItemAdmin(SnippetViewSet):
    model = DashboardItem
    menu_label = "Paralegal Dashboard"
    icon = "group"
    menu_order = 201
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_display = ("title", "link")
    search_fields = ("title",)


register_snippet(DashboardItemAdmin)


class ExternalNewsAdmin(SnippetViewSet):
    model = ExternalNews
    menu_label = "External News"
    icon = "pick"
    menu_order = 202
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_display = (
        "title",
        "published_date",
    )
    search_fields = ("title",)


register_snippet(ExternalNewsAdmin)


class ReportAdmin(SnippetViewSet):
    model = Report
    menu_label = "Reports"
    icon = "doc-full"
    menu_order = 203
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_display = (
        "title",
        BooleanColumn("is_featured"),
        UpdatedAtColumn(),
        LiveStatusTagColumn(),
    )
    list_filter = ("is_featured",)
    search_fields = ("title",)


register_snippet(ReportAdmin)
