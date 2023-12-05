from django.db import models
from django.apps import apps
from django.utils import timezone, dateformat
from pathlib import Path

PATH = apps.get_app_config("office").path
DATE_FORMAT = "l jS F Y" # e.g. Sunday 31st December 2023


class ShutdownTemplate(models.Model):
    def _get_call_default():
        return Path(PATH + "/shutdown/templates/call_template.txt").read_text()

    def _get_email_default():
        return Path(PATH + "/shutdown/templates/email_template.html").read_text()

    def _get_notice_default():
        return Path(PATH + "/shutdown/templates/notice_template.html").read_text()

    created_at = models.DateTimeField(default=timezone.now)
    call_text = models.TextField(default=_get_call_default, blank=False)
    email_html = models.TextField(default=_get_email_default, blank=False)
    notice_html = models.TextField(default=_get_notice_default, blank=False)


class Shutdown(models.Model):
    def _get_template_default():
        if not ShutdownTemplate.objects.exists():
            ShutdownTemplate.objects.create().save()
        return ShutdownTemplate.objects.latest("created_at").pk

    start_date = models.DateField(blank=False)
    end_date = models.DateField(blank=False)
    template = models.OneToOneField(
        ShutdownTemplate,
        blank=False,
        default=_get_template_default,
        on_delete=models.CASCADE,
    )

    @property
    def notice_html(self):
        start = dateformat.format(self.start_date, DATE_FORMAT)
        end = dateformat.format(self.end_date, DATE_FORMAT)
        return self.template.notice_html.format(start_date=start, end_date=end)
