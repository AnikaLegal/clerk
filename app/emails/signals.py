from core.services.slack import send_email_alert_slack, send_email_failure_alert_slack
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_q.tasks import async_task

from .models import Email, EmailState
from .service import receive_email_task, send_email_task


@receiver(post_save, sender=Email)
def save_email(sender, instance, **kwargs):
    # FIXME: Add tests
    email = instance
    if email.state == EmailState.READY_TO_SEND:
        async_task(send_email_task, email.pk)
    elif email.state == EmailState.RECEIVED:
        async_task(receive_email_task, email.pk)
    elif email.state == EmailState.INGESTED and not email.is_alert_sent:
        async_task(send_email_alert_slack, email.pk)
    elif email.state == EmailState.DELIVERY_FAILURE and not email.is_alert_sent:
        async_task(send_email_failure_alert_slack, email.pk)
