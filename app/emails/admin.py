from django.contrib import admin

from .models import Email, EmailAttachment


class AttachmentInline(admin.TabularInline):
    extra = 0
    model = EmailAttachment


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "state",
        "from_address",
        "to_address",
        "subject",
        "created_at",
        "is_alert_sent",
    )
    inlines = [AttachmentInline]
