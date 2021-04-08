from django.contrib import admin
from django.contrib.messages import constants as messages
from django_q.tasks import async_task

from .auth import refresh_tokens
from .models import AccessToken, ActionDocument
from .services.actionstep import upload_action_document


@admin.register(ActionDocument)
class ActionDocumentAdmin(admin.ModelAdmin):
    ordering = ("topic",)
    readonly_fields = ("modified_at", "created_at")
    list_display = ("id", "created_at", "document", "folder", "topic", "actionstep_id")
    list_filter = ("topic", "folder")

    actions = ["upload"]

    def upload(self, request, queryset):
        for doc in queryset:
            async_task(upload_action_document, doc.pk)

        self.message_user(request, "File upload started.", level=messages.INFO)

    upload.short_description = "Upload files"


@admin.register(AccessToken)
class AccessTokenAdmin(admin.ModelAdmin):
    change_list_template = "actionstep/access_token_changelist.html"

    ordering = ("-expires_at",)
    readonly_fields = ("expires_at", "created_at")
    list_display = ("id", "created_at", "expires_at", "is_active")

    actions = ["refresh"]

    def refresh(self, request, queryset):
        for access_token in queryset:
            async_task(refresh_tokens, access_token.pk)

        self.message_user(request, "Tokens request.", level=messages.INFO)

    refresh.short_description = "Refresh tokens"
