import json

from django.contrib import admin
from django.utils.safestring import mark_safe
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import JsonLexer

from questions.models import ImageUpload, Submission


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    ordering = ("-created_at",)
    readonly_fields = ("questions_json", "answers_json")
    exclude = ("questions", "answers")
    list_display = ("id", "created_at", "modified_at", "complete")

    def questions_json(self, instance):
        """Function to display pretty version of our data"""
        return dict_to_json_html(instance.questions)

    def answers_json(self, instance):
        return dict_to_json_html(instance.answers)


@admin.register(ImageUpload)
class ImageUploadAdmin(admin.ModelAdmin):
    ordering = ("-created_at",)
    list_display = ("id", "created_at", "modified_at", "image")


def dict_to_json_html(data):
    json_str = json.dumps(data, sort_keys=True, indent=2)
    formatter = HtmlFormatter(style="colorful")
    highlighted = highlight(json_str, JsonLexer(), formatter)
    style = "<style>" + formatter.get_style_defs() + "</style><br>"
    return mark_safe(style + highlighted)
