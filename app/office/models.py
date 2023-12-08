from django.db import models
from django.apps import apps
from django.utils import timezone, dateformat
from pathlib import Path

PATH = apps.get_app_config("office").path


class ClosureTemplate(models.Model):
    def _get_call_default():
        return Path(PATH + "/closure/templates/call_template.txt").read_text()

    def _get_email_default():
        return Path(PATH + "/closure/templates/email_template.html").read_text()

    def _get_notice_default():
        return Path(PATH + "/closure/templates/notice_template.html").read_text()

    created_at = models.DateTimeField(default=timezone.now)
    call_text = models.TextField(default=_get_call_default, blank=False)
    email_html = models.TextField(default=_get_email_default, blank=False)
    notice_html = models.TextField(default=_get_notice_default, blank=False)


class Closure(models.Model):
    def _get_template_default():
        if not ClosureTemplate.objects.exists():
            ClosureTemplate.objects.create().save()
        return ClosureTemplate.objects.latest("created_at").pk

    created_at = models.DateTimeField(default=timezone.now)
    start_date = models.DateField(blank=False)
    end_date = models.DateField(blank=False)
    template = models.OneToOneField(
        ClosureTemplate,
        blank=False,
        default=_get_template_default,
        on_delete=models.CASCADE,
    )
