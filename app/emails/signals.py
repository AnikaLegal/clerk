import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from django_q.tasks import async_task

from core.services.slack import send_email_alert_slack

from .models import Email, EmailState
from .service import send_email_task, receive_email_task

logger = logging.getLogger(__name__)


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
