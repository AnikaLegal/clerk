from django.contrib import admin

from utils.admin import dict_to_json_html

from .models import ClosedContact, JotformSubmission


@admin.register(ClosedContact)
class ClosedContactAdmin(admin.ModelAdmin):
    ordering = ("-created_at",)
    list_display = (
        "id",
        "name",
        "email",
        "topic",
        "created_at",
    )
    list_filter = ("topic",)


@admin.register(JotformSubmission)
class JotformSubmissionAdmin(admin.ModelAdmin):
    ordering = ("-created_at",)
    list_display = ("id", "form_name", "created_at")
    list_filter = ("form_name",)
    exclude = ("answers",)

    readonly_fields = ("form_name", "answers_json")

    def answers_json(self, instance):
        return dict_to_json_html(instance.answers)
