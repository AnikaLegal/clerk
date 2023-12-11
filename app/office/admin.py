from django.contrib import admin
from .models import Closure, ClosureTemplate


@admin.register(Closure)
class ClosureAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "template",
        "close_date",
        "reopen_date",
        "call_audio",
        "created_at",
    )


@admin.register(ClosureTemplate)
class ClosureAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "created_at",
    )
