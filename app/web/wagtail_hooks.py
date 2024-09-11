from django.utils.html import format_html
from django.templatetags.static import static

from wagtail import hooks
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

from .models import ExternalNews, DashboardItem


@hooks.register("insert_global_admin_css")
def global_admin_css():
    return format_html(
        '<link rel="stylesheet" href="{}">', static("web/styles/wagtail-admin.css")
    )


class ExternalNewsAdmin(SnippetViewSet):
    model = ExternalNews
    menu_label = "External News"
    icon = "pick"
    menu_order = 201
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_display = (
        "title",
        "published_date",
    )
    search_fields = ("title",)


register_snippet(ExternalNewsAdmin)


class DashboardItemAdmin(SnippetViewSet):
    model = DashboardItem
    menu_label = "Paralegal Dashboard"
    icon = "group"
    menu_order = 200
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_display = ("title", "link")
    search_fields = ("title",)


register_snippet(DashboardItemAdmin)
