from django.utils.html import format_html
from django.templatetags.static import static

from wagtail.core import hooks

from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from .models import ExternalNews


@hooks.register("insert_global_admin_css")
def global_admin_css():
    return format_html(
        '<link rel="stylesheet" href="{}">', static("web/styles/wagtail-admin.css")
    )


class ExternalNewsAdmin(ModelAdmin):
    model = ExternalNews
    menu_label = "External News"
    menu_icon = "pick"
    menu_order = 200
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_display = (
        "title",
        "published_date",
    )
    search_fields = ("title",)


modeladmin_register(ExternalNewsAdmin)
