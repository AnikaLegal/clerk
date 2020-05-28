import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from django_q.tasks import async_task

from questions.models import Submission
from questions.services.slack import send_submission_slack
from questions.services.submission import send_submission_email
from questions.services.actionstep import send_submission_actionstep

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Submission)
def save_submission(sender, instance, **kwargs):
    submission = instance
    if submission.complete:
        if not submission.is_alert_sent:
            logger.info("Dispatching alert task for Submission<%s]>", submission.id)
            async_task(send_submission_slack, str(submission.pk))
        if not submission.is_data_sent:
            logger.info("Dispatching data task for Submission<%s]>", submission.id)
            async_task(send_submission_email, str(submission.pk))
        if not submission.is_case_sent:
            logger.info("Dispatching Actionstep task for Submission<%s]>", submission.id)
            async_task(send_submission_actionstep, str(submission.pk))
