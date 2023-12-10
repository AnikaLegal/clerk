from django.apps import apps
from django.conf import settings
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils import timezone
from django_cleanup import cleanup
from pathlib import Path
from storages.backends.s3boto3 import S3Boto3Storage

PATH = apps.get_app_config("office").path


@cleanup.select
class ClosureTemplate(models.Model):
    def _get_call_default():
        return Path(PATH + "/closure/templates/call_template.txt").read_text()

    def _get_email_default():
        return Path(PATH + "/closure/templates/email_template.html").read_text()

    def _get_notice_default():
        return Path(PATH + "/closure/templates/notice_template.html").read_text()

    def _get_file_name(instance, name):
        now = timezone.localdate()
        return "office_closure_call_audio_{year}_{month}_{day}{ext}".format(
            year=now.year, month=now.month, day=now.day, ext=Path(name).suffix
        )

    def _get_storage():
        return S3Boto3Storage(
            bucket_name=settings.TWILIO_AUDIO_BUCKET_NAME,
            file_overwrite=False,
        )

    created_at = models.DateTimeField(default=timezone.now)
    call_audio = models.FileField(
        blank=True,
        null=True,
        storage=_get_storage,
        upload_to=_get_file_name,
    )
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
