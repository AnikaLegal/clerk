from django_q.tasks import async_task
from django.contrib import admin
from django.contrib.messages import constants as messages

from core.services.slack import send_submission_slack
from actionstep.services.actionstep import send_submission_actionstep
from utils.admin import admin_link, dict_to_json_html

from .models import FileUpload, Submission, Client, Person, Tenancy


@admin.register(FileUpload)
class FileUploadAdmin(admin.ModelAdmin):
    ordering = ("-created_at",)
    list_display = ("id", "created_at", "submission_link", "file")
    list_select_related = ("submission",)

    @admin_link("submission", "Submission")
    def submission_link(self, submission):
        return submission.id


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
        "is_reminder_sent",
    )
    list_filter = ("is_eligible",)


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    ordering = ("-created_at",)
    readonly_fields = ("answers_json",)
    exclude = ("answers",)
    list_display = (
        "id",
        "topic_pretty",
        "client_link",
        "complete",
        "is_alert_sent",
        "is_case_sent",
        "created_at",
    )
    list_filter = (
        "topic",
        "complete",
        "is_alert_sent",
        "is_case_sent",
    )

    list_select_related = ("client",)

    def topic_pretty(self, sub):
        return sub.topic.replace("_", " ").title()

    topic_pretty.short_description = "topic"

    @admin_link("client", "Client")
    def client_link(self, client):
        return client.get_full_name()

    actions = ["notify", "integrate"]

    def integrate(self, request, queryset):
        for submission in queryset:
            async_task(send_submission_actionstep, str(submission.pk))

        self.message_user(request, "Integrations sent.", level=messages.INFO)

    integrate.short_description = "Integrate with external systems"

    def notify(self, request, queryset):
        for submission in queryset:
            async_task(send_submission_slack, str(submission.pk))

        self.message_user(request, "Notifications sent.", level=messages.INFO)

    notify.short_description = "Send notifications"

    def answers_json(self, instance):
        return dict_to_json_html(instance.answers)


@admin.register(Tenancy)
class TenancyAdmin(admin.ModelAdmin):
    ordering = ("-created_at",)
    list_display = (
        "id",
        "address",
        "client_link",
        "landlord_link",
        "agent_link",
        "created_at",
    )
    list_select_related = (
        "client",
        "landlord",
        "agent",
    )

    @admin_link("client", "Client")
    def client_link(self, client):
        return client.get_full_name()

    @admin_link("landlord", "Landlord")
    def landlord_link(self, landlord):
        return landlord.full_name

    @admin_link("agent", "Agent")
    def agent_link(self, agent):
        return agent.full_name
