from django.contrib import admin

from .models import Email, EmailAttachment


class AttachmentInline(admin.TabularInline):
    extra = 0
    model = EmailAttachment


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "created_at",
        "from_addr",
        "to_addr",
        "subject",
    )
    inlines = [AttachmentInline]
