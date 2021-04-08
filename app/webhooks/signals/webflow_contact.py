import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from django_q.tasks import async_task

from webhooks.models import WebflowContact
from webhooks.services.slack import send_webflow_contact_slack

logger = logging.getLogger(__name__)


@receiver(post_save, sender=WebflowContact)
def save_webflow_contact(sender, instance, **kwargs):
    contact = instance
    if not contact.is_alert_sent:
        logger.info("Dispatching on-save tasks for WebflowContact<%s]>", contact.id)
        async_task(send_webflow_contact_slack, str(contact.pk))
