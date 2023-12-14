from django.contrib import admin
from utils.admin import admin_link
from .models import Closure, ClosureTemplate


@admin.register(Closure)
class ClosureAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "template_link",
        "close_date",
        "reopen_date",
        "call_audio",
        "created_at",
    )

    @admin_link("template", "ClosureTemplate")
    def template_link(self, template):
        return template.pk


@admin.register(ClosureTemplate)
class ClosureAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "created_at",
    )
