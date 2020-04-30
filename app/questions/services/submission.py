import logging

import weasyprint
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from questions.models import ImageUpload, Submission

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


def create_pdf(submission):
    """
    Returns a PDF file string.
    """
    # Get questions from sections
    fields = {}
    for section in submission.questions:
        for form in section["forms"]:
            for field in form["fields"]:
                fs = field.get("fields", [field])
                for f in fs:
                    fields[f["name"]] = f

    # Pull out image and answers
    images = []
    answers = []
    for answer in submission.answers:
        answer, name = answer.get("answer", ""), answer.get("name", "")
        field = fields[name]
        if field["type"] == "FILE":
            ids = [image["id"] for image in answer]
            images += [
                image_upload.image for image_upload in ImageUpload.objects.filter(pk__in=ids).all()
            ]
        else:
            answers.append(
                {
                    "name": name.lower().replace("_", " ").capitalize(),
                    "prompt": field.get("prompt", ""),
                    "answers": answer if type(answer) is list else [answer],
                }
            )

    context = {"submission": submission, "answers": answers, "images": images}
    pdf_html_str = render_to_string("client-intake.html", context=context)
    pdf_bytes = weasyprint.HTML(string=pdf_html_str).write_pdf()
    return pdf_bytes
