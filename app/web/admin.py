from django.contrib import admin

from .models import WebRedirect


@admin.register(WebRedirect)
class WebRedirectAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "source_path",
        "destination_path",
        "is_permanent",
    )
