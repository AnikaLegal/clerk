from django.contrib import admin
from django.db import models
from django.forms import Textarea
from task.models import (
    Task,
    TaskActivity,
    TaskAttachment,
    TaskComment,
    TaskEvent,
    TaskTemplate,
    TaskTrigger,
)
from utils.admin import admin_link


class TaskTemplateInline(admin.TabularInline):
    model = TaskTemplate
    extra = 0
    fields = (
        "type",
        "name",
        "description",
        "due_in",
        "is_urgent",
        "is_approval_required",
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
        "due_in",
        "is_urgent",
        "is_approval_required",
    )


class TaskCommentInline(admin.TabularInline):
    model = TaskComment
    extra = 0
    show_change_link = True


class TaskAttachmentInline(admin.TabularInline):
    model = TaskAttachment
    extra = 0
    show_change_link = True


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    inlines = (TaskCommentInline, TaskAttachmentInline)
    list_display = (
        "id",
        "type",
        "name",
        "assigned_to_link",
        "assignee_role",
        "status",
        "due_at",
        "is_urgent",
        "is_approval_required",
        "is_open",
        "is_suspended",
    )
    readonly_fields = (
        "is_notify_pending",
        "is_system_update",
        "is_open",
        "is_suspended",
    )

    @admin_link("assigned_to", "Assigned To")
    def assigned_to_link(self, user):
        return user if user else None


@admin.register(TaskActivity)
class TaskActivityAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "task_link",
        "created_at",
    )

    @admin_link("task", "Task")
    def task_link(self, task):
        return task if task else None

    @admin_link("user", "User")
    def user_link(self, user):
        return user if user else None


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "text",
        "task_link",
        "creator_link",
        "created_at",
    )

    @admin_link("task", "Task")
    def task_link(self, task):
        return task if task else None

    @admin_link("creator", "Creator")
    def creator_link(self, user):
        return user if user else None


@admin.register(TaskEvent)
class TaskEventAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "type",
        "task_link",
        "user_link",
        "created_at",
    )

    @admin_link("task", "Task")
    def task_link(self, task):
        return task if task else None

    @admin_link("user", "User")
    def user_link(self, user):
        return user if user else None



@admin.register(TaskAttachment)
class TaskAttachmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "file",
        "content_type",
        "created_at",
        "task_link",
    )

    @admin_link("task", "Task")
    def task_link(self, task):
        return task if task else None