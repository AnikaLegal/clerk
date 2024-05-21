from django.contrib import admin
from django.forms import Textarea
from django.db import models

from task.models import Task, TaskTrigger, TaskTemplate, TaskComment
from utils.admin import admin_link


class TaskTemplateInline(admin.TabularInline):
    model = TaskTemplate
    extra = 0
    fields = (
        "type",
        "name",
        "description",
        "_order",
    )
    formfield_overrides = {
        models.TextField: {"widget": Textarea(attrs={"rows": 4, "cols": 80})},
    }
    readonly_fields = ("_order",)
    show_change_link = True


@admin.register(TaskTrigger)
class TaskTriggerAdmin(admin.ModelAdmin):
    inlines = (TaskTemplateInline,)
    list_display = (
        "id",
        "topic",
        "event",
        "event_stage",
        "tasks_assignment_role",
    )
    ordering = ("topic",)


@admin.register(TaskTemplate)
class TaskTemplateAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "type",
        "name",
        "description",
    )


class TaskCommentInline(admin.TabularInline):
    model = TaskComment
    extra = 0
    show_change_link = True


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    inlines = (TaskCommentInline,)
    list_display = (
        "id",
        "type",
        "name",
        "owner_link",
        "assigned_to_link",
        "status",
        "is_open",
        "is_suspended",
    )
    readonly_fields = (
        "is_notify_pending",
        "is_system_update",
        "is_open",
        "is_suspended",
        "prev_owner_role",
    )

    @admin_link("owner", "Owner")
    def owner_link(self, user):
        return user if user else None

    @admin_link("assigned_to", "Assigned To")
    def assigned_to_link(self, user):
        return user if user else None


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "type",
        "text",
        "task_link",
        "creator_link",
    )

    @admin_link("task", "Task")
    def task_link(self, task):
        return task if task else None

    @admin_link("creator", "Creator")
    def creator_link(self, user):
        return user if user else None
