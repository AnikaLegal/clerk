from django.contrib import admin
from .models import Shutdown, ShutdownTemplate


@admin.register(Shutdown)
class ShutdownAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "start_date",
        "end_date",
    )


@admin.register(ShutdownTemplate)
class ShutdownAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "created_at",
    )
