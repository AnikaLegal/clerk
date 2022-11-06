from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "topic",
        "created_at",
    )
