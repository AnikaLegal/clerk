from django.contrib import admin

from .models import WebflowContact


@admin.register(WebflowContact)
class WebflowContactAdmin(admin.ModelAdmin):
    ordering = ("-created_at",)
    list_display = ("id", "name", "email", "phone", "created_at", "modified_at")
