import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from django_q.tasks import async_task

from core.models import Submission
from core.services.submission import process_submission

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Submission)
def save_submission(sender, instance, **kwargs):
    sub = instance
    if sub.is_complete and not sub.is_processed:
        logger.info("Dispatching processing task for Submission<%s>", sub.pk)
        async_task(process_submission, str(sub.pk))
