from django.contrib import admin

from utils.admin import dict_to_json_html
from questions.models import FileUpload, ImageUpload, Submission


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    ordering = ("-created_at",)
    readonly_fields = ("answers_json",)
    exclude = ("questions", "answers")
    list_display = (
        "id",
        "topic",
        "created_at",
        "modified_at",
        "num_answers",
        "complete",
        "is_case_sent",
        "is_reminder_sent",
    )
    list_filter = (
        "topic",
        "complete",
        "is_reminder_sent",
    )

    def answers_json(self, instance):
        return dict_to_json_html(instance.answers)


@admin.register(ImageUpload)
class ImageUploadAdmin(admin.ModelAdmin):
    ordering = ("-created_at",)
    list_display = ("id", "created_at", "modified_at", "image")


@admin.register(FileUpload)
class FileUploadAdmin(admin.ModelAdmin):
    ordering = ("-created_at",)
    list_display = ("id", "created_at", "modified_at", "file")
