import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from questions.models import Submission

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Submission)
def save_submission(sender, instance, **kwargs):
    submission = instance
    logger.info('SAVE SUBMISSION SIGNAL')
