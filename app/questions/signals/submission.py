import logging

from django.db.models.signals import pre_save
from django.dispatch import receiver

from questions.models import Submission
from questions.services.submission import send_submission_email

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Submission)
def save_submission(sender, instance, **kwargs):
    submission = instance
    if submission.complete:
        send_submission_email(submission)
