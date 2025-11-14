from auditlog.mixins import LogEntryAdminMixin
from core.services.slack import send_issue_slack
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.auth import get_user_model
from django.contrib.messages import constants as messages
from django_q.tasks import async_task
from utils.admin import admin_link, dict_to_json_html

from .models import (
    AuditEvent,
    Client,
    DocumentTemplate,
    FileUpload,
    Issue,
    IssueDate,
    IssueEvent,
    IssueNote,
    Person,
    Service,
    ServiceEvent,
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
    readonly_fields = ("answers_json",)

    def answers_json(self, instance):
        return dict_to_json_html(instance.answers)


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
    readonly_fields = ("answers_json", "submission")
    exclude = ("answers",)
    list_display = (
        "id",
        "fileref",
        "topic",
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
        "is_deleted",
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


@admin.register(DocumentTemplate)
class DocumentTemplateAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "topic",
        "file",
    )
    list_filter = ("topic",)


@admin.register(IssueDate)
class IssueDateAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "issue_link",
        "type",
        "date",
        "notes",
        "is_reviewed",
        "created_at",
    )
    list_filter = ("type", "is_reviewed")
    ordering = ("-created_at",)

    @admin_link("issue", "Issue")
    def issue_link(self, issue):
        return issue.fileref if issue else None


class ResourceTypeFilter(SimpleListFilter):
    title = "Resource Type"
    parameter_name = "resource_type"

    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)
        types = qs.values_list(
            "log_entry__content_type_id", "log_entry__content_type__model"
        )
        return list(types.order_by("log_entry__content_type__model").distinct())

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        return queryset.filter(log_entry__content_type_id=self.value())


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin, LogEntryAdminMixin):
    list_display = (
        "created",
        "action",
        "resource_url",
        "msg_short",
        "user_url",
    )
    list_filter = ["log_entry__action", ResourceTypeFilter]
    list_select_related = ["log_entry__content_type", "log_entry__actor"]
    search_fields = [
        "log_entry__timestamp",
        "log_entry__object_repr",
        "log_entry__changes",
        "log_entry__actor__first_name",
        "log_entry__actor__last_name",
        f"log_entry__actor__{get_user_model().USERNAME_FIELD}",
    ]
    fieldsets = [
        (None, {"fields": ["created", "user_url", "resource_url"]}),
        ("Changes", {"fields": ["action", "msg"]}),
    ]
    readonly_fields = ["created", "resource_url", "action", "user_url", "msg"]

    def action(self, obj):
        obj = obj.log_entry
        return obj.get_action_display()

    def created(self, obj):
        return super().created(obj.log_entry)

    @admin.display(description="resource")
    def resource_url(self, obj):
        return super().resource_url(obj.log_entry)

    @admin.display(description="changes")
    def msg_short(self, obj):
        return super().msg_short(obj.log_entry)

    @admin.display(description="user")
    def user_url(self, obj):
        return super().user_url(obj.log_entry)

    @admin.display(description="changes")
    def msg(self, obj):
        return super().msg(obj.log_entry)
