import logging

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django_q.tasks import async_task

from webhooks.models import WebflowContact
from blacklist.service import is_blacklisted
from webhooks.services.slack import send_webflow_contact_slack

BLACKLIST_COMMENT = "The contact's email and/or phone number are blacklisted."

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=WebflowContact)
def pre_save_webflow_contact(sender, instance, **kwargs):
    contact = instance

    if is_blacklisted(email=contact.email, phone=contact.phone):
        logger.info("WebflowContact<%s> is blacklisted", contact.id)
        contact.is_alert_sent = True  # Nasty, prevent the alert being sent later.
        contact.requires_callback = False
        contact.comments = BLACKLIST_COMMENT


@receiver(post_save, sender=WebflowContact)
def post_save_webflow_contact(sender, instance, **kwargs):
    contact = instance

    if not contact.is_alert_sent:
        logger.info("Dispatching on-save tasks for WebflowContact<%s>", contact.id)
        async_task(send_webflow_contact_slack, str(contact.pk))
