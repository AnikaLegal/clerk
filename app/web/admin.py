from django.contrib import admin

from .models import WebRedirect, ContentFeedback


@admin.register(WebRedirect)
class WebRedirectAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "source_path",
        "destination_path",
        "is_permanent",
    )


@admin.register(ContentFeedback)
class ContentFeedbackAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "score",
        "page_id",
    )
