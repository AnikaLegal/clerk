import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from questions.models import ImageUpload, Submission

logger = logging.getLogger(__name__)


def send_submission_email(submission_pk):
    """
    Send a submission alert email with data included.
    """
    submission = Submission.objects.get(pk=submission_pk)
    subject = f"Client intake submission {str(submission.id)}"
    if settings.EMAIL_PREFIX:
        subject = f"[{settings.EMAIL_PREFIX}] {subject}"

    body = subject + "\n\n"
    answers = submission.answers
    questions = submission.questions
    if not answers or not questions:
        logger.error("Submission[%s] has insufficient data", submission.id)

    # Get questions from sections
    fields = {}
    for section in questions:
        for form in section["forms"]:
            for field in form["fields"]:
                fs = field.get("fields", [field])
                for f in fs:
                    fields[f["name"]] = f

    # Assume answer is a list of dicts with a pretty specific structure.
    # See tests
    images = []
    for answer in answers:
        answer, name = answer.get("answer", ""), answer.get("name", "")
        field = fields[name]
        if field["type"] == "FILE":
            ids = [image["id"] for image in answer]
            images += [
                image_upload.image for image_upload in ImageUpload.objects.filter(pk__in=ids).all()
            ]
        else:
            body += name + " " + field.get("prompt", "") + "\n\n"
            body += repr(answer) + "\n\n"

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
