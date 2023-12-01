from django.db import models
from django.utils import timezone
from pathlib import Path
from django.apps import apps

PATH = apps.get_app_config("office").path


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
        if ShutdownTemplate.objects.count() == 0:
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
