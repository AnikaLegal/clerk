import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from django_q.tasks import async_task

from actionstep.models import ActionDocument
from actionstep.services.actionstep import upload_action_document

logger = logging.getLogger(__name__)


@receiver(post_save, sender=ActionDocument)
def save_document(sender, instance, **kwargs):
    # FIXME: add tests
    doc = instance
    if not doc.actionstep_id:
        logger.info("Dispatching upload task for ActionDocument<%s]>", doc.id)
        async_task(upload_action_document, doc.pk)
