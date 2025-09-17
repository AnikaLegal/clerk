from django.contrib import admin
from django_q.tasks import async_task
from django.contrib.messages import constants as messages

from .models import Email, EmailAttachment, EmailTemplate
from .service.receive import ingest_email_task


class AttachmentInline(admin.TabularInline):
    extra = 0
    model = EmailAttachment


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_filter = ("state",)

    list_display = (
        "id",
        "state",
        "from_address",
        "to_address",
        "subject",
        "created_at",
        "is_alert_sent",
    )
    readonly_fields = ("thread_name", "received_data", "received_data_hash")
    inlines = [AttachmentInline]
    actions = ["ingest"]

    def ingest(self, request, queryset):
        for email in queryset:
            async_task(ingest_email_task, str(email.pk))

        self.message_user(
            request, "Email ingestion task dispatched.", level=messages.INFO
        )

    ingest.short_description = "Ingest received emails."


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "topic",
        "name",
        "created_at",
    )
