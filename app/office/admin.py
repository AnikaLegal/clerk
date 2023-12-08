from django.contrib import admin
from .models import Closure, ClosureTemplate


@admin.register(Closure)
class ClosureAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "start_date",
        "end_date",
        "created_at",
    )


@admin.register(ClosureTemplate)
class ClosureAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "created_at",
    )
