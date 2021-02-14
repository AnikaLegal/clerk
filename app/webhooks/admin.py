from django.contrib import admin

from .models import WebflowContact, JotformSubmission
from utils.admin import dict_to_json_html


@admin.register(WebflowContact)
class WebflowContactAdmin(admin.ModelAdmin):
    ordering = ("-created_at",)
    list_display = (
        "id",
        "name",
        "referral",
        "email",
        "phone",
        "created_at",
        "requires_callback",
        "number_callbacks",
        "comments",
    )
    list_filter = ("referral",)


@admin.register(JotformSubmission)
class JotformSubmissionAdmin(admin.ModelAdmin):
    ordering = ("-created_at",)
    list_display = ("id", "form_name", "created_at")
    list_filter = ("form_name",)
    exclude = ("answers",)

    readonly_fields = ("form_name", "answers_json")

    def answers_json(self, instance):
        return dict_to_json_html(instance.answers)
