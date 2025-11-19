from django.contrib import admin

from .models import WebRedirect, ContentFeedback, Report, DocumentLog


@admin.register(ContentFeedback)
class ContentFeedbackAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "score",
        "page_id",
    )


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "is_featured",
    )


@admin.register(DocumentLog)
class DocumentLogAdmin(admin.ModelAdmin):
    def has_change_permission(self, request, obj=None):
        # Disable editing.
        return False

    list_display = (
        "document",
        "state",
        "sector",
        "referrer",
    )
    list_filter = (
        "state",
        "sector",
        "referrer",
        "document",
    )


@admin.register(WebRedirect)
class WebRedirectAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "source_path",
        "destination_path",
        "is_permanent",
    )
