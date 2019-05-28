import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from questions.models import ImageUpload

logger = logging.getLogger(__name__)


def send_submission_email(submission):
    """
    Send a submission alert email with data included.
    """
    subject = f"Client intake submission {str(submission.id)}"
    if settings.DEBUG:
        subject = "[TEST] " + subject

    body = subject + "\n\n"
    answers = submission.data["answers"]
    questions = submission.data["questions"]
    if not answers or not questions:
        logger.error("Submission[%s] has insufficient data", submission.id)

    # Assume answer is a list of dicts with a pretty specific structure.
    images = []
    for answer in answers:
        question = questions[answer["name"]]
        if question["type"] == "FILE":
            ids = [i["id"] for i in answer["answer"]]
            images += [i.image for i in ImageUpload.objects.filter(pk__in=ids).all()]
        else:
            body += question["name"] + " " + question.get("prompt", "NO PROMPT") + "\n\n"
            body += repr(answer["answer"]) + "\n\n"

    logger.info("Sending email for Submission[%s]", submission.id)
    email = EmailMultiAlternatives(
        subject=subject,
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=settings.SUBMISSION_EMAILS,
    )
    for image in images:
        email.attach(image.name.split("/")[-1], image.read())

    email.send(fail_silently=False)
