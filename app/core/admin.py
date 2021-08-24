from django.contrib import admin
from django.contrib.messages import constants as messages
from django_q.tasks import async_task

from actionstep.services.actionstep import send_issue_actionstep
from core.services.slack import send_issue_slack
from utils.admin import admin_link, dict_to_json_html

from .models import Client, FileUpload, Issue, IssueNote, Person, Submission, Tenancy


@admin.register(IssueNote)
class IssueNoteAdmin(admin.ModelAdmin):
    ordering = ("-created_at",)
    list_display = (
        "id",
        "created_at",
        "creator",
        "note_type",
        "actionstep_id",
    )


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    ordering = ("-created_at",)
    list_display = (
        "id",
        "created_at",
        "modified_at",
        "is_complete",
        "is_processed",
        "is_reminder_sent",
    )


@admin.register(FileUpload)
class FileUploadAdmin(admin.ModelAdmin):
    ordering = ("-created_at",)
    list_display = ("id", "created_at", "issue_link", "file")
    list_select_related = ("issue",)

    @admin_link("issue", "Issue")
    def issue_link(self, issue):
        return issue.id if issue else None


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
        "referrer_type",
        "referrer",
        "created_at",
    )
    list_filter = ("referrer_type",)


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    ordering = ("-created_at",)
    readonly_fields = ("answers_json",)
    exclude = ("answers",)
    list_display = (
        "id",
        "topic_pretty",
        "client_link",
        "is_alert_sent",
        "is_case_sent",
        "created_at",
    )
    list_filter = ("topic", "is_alert_sent", "is_case_sent")

    list_select_related = ("client",)

    def topic_pretty(self, sub):
        return sub.topic.replace("_", " ").title()

    topic_pretty.short_description = "topic"

    @admin_link("client", "Client")
    def client_link(self, client):
        return client.get_full_name()

    actions = ["notify", "integrate"]

    def integrate(self, request, queryset):
        for issue in queryset:
            async_task(send_issue_actionstep, str(issue.pk))

        self.message_user(request, "Integrations sent.", level=messages.INFO)

    integrate.short_description = "Integrate with external systems"

    def notify(self, request, queryset):
        for issue in queryset:
            async_task(send_issue_slack, str(issue.pk))

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
        "postcode",
        "suburb",
        "client_link",
        "landlord_link",
        "agent_link",
        "created_at",
    )
    list_select_related = ("client", "landlord", "agent")

    @admin_link("client", "Client")
    def client_link(self, client):
        return client.get_full_name()

    @admin_link("landlord", "Landlord")
    def landlord_link(self, landlord):
        return landlord.full_name

    @admin_link("agent", "Agent")
    def agent_link(self, agent):
        return agent.full_name
