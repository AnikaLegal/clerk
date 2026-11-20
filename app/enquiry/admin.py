from django.contrib import admin

from .models import Callback, Enquiry


class CallbackInline(admin.TabularInline):
    model = Callback
    extra = 0
    fields = ("created_at", "logged_by", "is_answered", "summary")
    readonly_fields = fields


@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    ordering = ("-created_at",)
    list_display = (
        "id",
        "source",
        "name",
        "email",
        "phone",
        "topic",
        "created_at",
        "requires_callback",
        "number_callbacks",
    )
    list_filter = ("source", "requires_callback")
    search_fields = ("name", "email", "phone")
    inlines = (CallbackInline,)
