import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from django_q.tasks import async_task

from emails.models import NoEmailAdmin
from core.services.submission import process_noemail

logger = logging.getLogger(__name__)


@receiver(post_save, sender=NoEmailAdmin)
def save_noemail(sender, instance, **kwargs):
    sub = instance
    if sub.is_complete and not sub.is_processed:
        logger.info("Dispatching processing task for NoEmail<%s]>", sub.pk)
        async_task(process_noemail, str(sub.pk))
