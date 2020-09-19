import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from django_q.tasks import async_task

from core.models import Submission
from core.services.slack import send_submission_slack
from actionstep.services.actionstep import send_submission_actionstep

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Submission)
def save_submission(sender, instance, **kwargs):
    sub = instance
    if sub.complete:
        if not sub.is_alert_sent:
            logger.info("Dispatching alert task for Submission<%s]>", sub.id)
            async_task(send_submission_slack, str(sub.pk))
        if not sub.is_case_sent:
            logger.info("Dispatching Actionstep task for Submission<%s]>", sub.id)
            async_task(send_submission_actionstep, str(sub.pk))
