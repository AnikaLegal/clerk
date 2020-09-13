import json

from django_q.tasks import async_task
from django.contrib import admin
from django.contrib.messages import constants as messages
from django.utils.safestring import mark_safe
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import JsonLexer

from questions.services.slack import send_submission_slack
from questions.services.submission import send_submission_email
from questions.services.actionstep import send_submission_actionstep

from .models import FileUpload, Submission, Client, Person


@admin.register(FileUpload)
class FileUploadAdmin(admin.ModelAdmin):
    ordering = ("-created_at",)
    list_display = ("id", "created_at", "modified_at", "file")


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    ordering = ("-created_at",)
    list_display = ("id", "full_name", "email", "phone_number")


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    ordering = ("-created_at",)
    list_display = (
        "id",
        "first_name",
        "last_name",
        "email",
        "phone_number",
        "is_eligible",
        "created_at",
    )
    list_filter = ("is_eligible",)


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    ordering = ("-created_at",)
    readonly_fields = ("answers_json",)
    list_display = (
        "id",
        "topic",
        "created_at",
        "modified_at",
        "complete",
        "is_alert_sent",
        "is_data_sent",
        "is_case_sent",
        "is_reminder_sent",
    )
    list_filter = (
        "topic",
        "complete",
        "is_alert_sent",
        "is_data_sent",
        "is_case_sent",
        "is_reminder_sent",
    )

    actions = ["notify", "integrate"]

    def integrate(self, request, queryset):
        for submission in queryset:
            async_task(send_submission_actionstep, str(submission.pk))

        self.message_user(request, "Integrations sent.", level=messages.INFO)

    integrate.short_description = "Integrate with external systems"

    def notify(self, request, queryset):
        for submission in queryset:
            async_task(send_submission_email, str(submission.pk))
            async_task(send_submission_slack, str(submission.pk))

        self.message_user(request, "Notifications sent.", level=messages.INFO)

    notify.short_description = "Send notifications"

    def answers_json(self, instance):
        return dict_to_json_html(instance.answers)


def dict_to_json_html(data):
    json_str = json.dumps(data, sort_keys=True, indent=2)
    formatter = HtmlFormatter(style="colorful")
    highlighted = highlight(json_str, JsonLexer(), formatter)
    style = "<style>" + formatter.get_style_defs() + "</style><br>"
    return mark_safe(style + highlighted)
