import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from questions.models import Submission

from .pdf import create_pdf

logger = logging.getLogger(__name__)


def send_submission_email(submission_pk):
    """
    Send a submission alert email with data included.
    """
    submission = Submission.objects.get(pk=submission_pk)
    subject = f"Client intake submission {submission.topic} {str(submission.id)}"
    if settings.EMAIL_PREFIX:
        subject = f"[{settings.EMAIL_PREFIX}] {subject}"

    body = subject + "\n\n"
    if not submission.answers or not submission.questions:
        logger.error("Submission[%s] has insufficient data", submission.id)

    body = subject + "\nSee attached PDF for client submission details."

    logger.info("Sending email for Submission<%s]>", submission.id)
    email = EmailMultiAlternatives(
        subject=subject,
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=settings.SUBMISSION_EMAILS,
    )
    pdf_str = create_pdf(submission)
    pdf_filename = f"client-intake-{submission_pk}.pdf"
    email.attach(pdf_filename, pdf_str)
    email.send(fail_silently=False)
    # Mark request as sent
    Submission.objects.filter(pk=submission.pk).update(is_data_sent=True)
