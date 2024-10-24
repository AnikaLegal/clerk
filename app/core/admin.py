from core.services.slack import send_issue_slack
from django.contrib import admin
from django.contrib.messages import constants as messages
from django_q.tasks import async_task
from utils.admin import admin_link, dict_to_json_html

from .models import (
    Client,
    FileUpload,
    Issue,
    IssueEvent,
    IssueNote,
    Service,
    ServiceEvent,
    Person,
    Submission,
    Tenancy,
)


@admin.register(IssueEvent)
class IssueEventAdmin(admin.ModelAdmin):
    ordering = ("-created_at",)
    list_display = (
        "id",
        "created_at",
        "event_type",
        "issue_id",
    )


@admin.register(IssueNote)
class IssueNoteAdmin(admin.ModelAdmin):
    ordering = ("-created_at",)
    list_display = (
        "id",
        "created_at",
        "creator",
        "note_type",
        "actionstep_id",
        "issue_id",
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
        "created_at",
    )


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    ordering = ("-created_at",)
    readonly_fields = ("answers_json",)
    exclude = ("answers",)
    list_display = (
        "id",
        "fileref",
        "topic_pretty",
        "client_link",
        "is_alert_sent",
        "is_case_sent",
        "is_sharepoint_set_up",
        "referrer_type",
        "referrer",
        "created_at",
    )
    list_filter = ("topic", "is_alert_sent", "is_case_sent", "referrer_type")

    list_select_related = ("client",)

    def topic_pretty(self, sub):
        return sub.topic.replace("_", " ").title()

    topic_pretty.short_description = "topic"

    @admin_link("client", "Client")
    def client_link(self, client):
        return client.get_full_name()

    actions = ["notify"]

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
        "landlord_link",
        "agent_link",
        "created_at",
    )
    list_select_related = ("landlord", "agent")

    @admin_link("landlord", "Landlord")
    def landlord_link(self, landlord):
        return landlord.full_name

    @admin_link("agent", "Agent")
    def agent_link(self, agent):
        return agent.full_name


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "category",
        "type",
        "started_at",
        "finished_at",
    )
    ordering = ("-created_at",)


@admin.register(ServiceEvent)
class ServiceEventAdmin(admin.ModelAdmin):
    ordering = ("-created_at",)
    list_display = (
        "id",
        "event_type",
        "service_link",
        "user_link",
    )

    @admin_link("service", "Service")
    def service_link(self, service):
        return service.id if service else None

    @admin_link("user", "User")
    def user_link(self, user):
        return user.get_full_name()
