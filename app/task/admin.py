from django.contrib import admin
from django.forms import Textarea
from django.db import models
from task.models import Task, TaskTrigger, TaskTemplate

admin.site.register(Task)
admin.site.register(TaskTemplate)


class TemplateInline(admin.TabularInline):
    model = TaskTemplate
    extra = 0
    fields = (
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
    inlines = (TemplateInline,)
