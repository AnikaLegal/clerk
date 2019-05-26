import logging

from django.conf import settings

from .mailer import Email
from questions.models import ImageUpload

logger = logging.getLogger(__name__)


def send_submission_email(submission):
    """
    Send a submission alert email with data included.
    """
    subject = f"Client intake submission {str(submission.id)}"
    attached_files = []
    if settings.DEBUG:
        subject = "[TEST] " + subject

    body = subject + "\n\n"
    answers = submission.data["answers"]
    questions = submission.data["questions"]
    if not answers or not questions:
        logger.error("Submission[%s] has insufficient data", submission.id)

    # Assume answer is a list of dicts with a pretty specific structure.
    for answer in answers:
        question = questions[answer["name"]]
        if question["type"] == "FILE":
            ids = [i["id"] for i in answer["answer"]]
            attached_files += [
                i.image.file.file for i in ImageUpload.objects.filter(pk__in=ids).all()
            ]
        else:
            body += question["name"] + " " + question.get("prompt", "NO PROMPT") + "\n\n"
            body += repr(answer["answer"]) + "\n\n"

    logger.info("Sending email for Submission[%s]", submission.id)
    (
        Email(subject=subject, recipients=settings.SUBMISSION_EMAILS)
        .with_text_body(body)
        .with_files(attached_files)
        .send()
    )
