from django.contrib import admin

from .models import WebRedirect, ContentFeeback


@admin.register(WebRedirect)
class WebRedirectAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "source_path",
        "destination_path",
        "is_permanent",
    )


@admin.register(ContentFeeback)
class ContentFeebackAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "score",
        "page_id",
    )
