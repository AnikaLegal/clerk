import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from django_q.tasks import async_task

from core.models import Submission
from actionstep.services.actionstep import send_submission_actionstep

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Submission)
def save_submission(sender, instance, **kwargs):
    submission = instance
    if submission.complete and not submission.is_case_sent:
        logger.info("Dispatching Actionstep task for Submission<%s]>", submission.id)
        async_task(send_submission_actionstep, str(submission.pk))
