import logging

import pdfkit
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
    subject = f"Client intake submission {str(submission.id)}"
    if settings.EMAIL_PREFIX:
        subject = f"[{settings.EMAIL_PREFIX}] {subject}"

    body = subject + "\n\n"
    if not submission.answers or not submission.questions:
        logger.error("Submission[%s] has insufficient data", submission.id)

    # Extract the images
    images = []
    for answer in answers:
        field = fields[name]
        if field["type"] == "FILE":
            ids = [image["id"] for image in answer]
            images += [
                image_upload.image for image_upload in ImageUpload.objects.filter(pk__in=ids).all()
            ]

    image_list_str = ""
    if images:
        image_urls = [f"\n- {image.url}" for image in images]
        image_list_str = f"\n\nAttached images:\n{image_urls}\n"

    body_kwargs = {
        "subject": subject,
        "image_list": image_list_str,
    }
    body = subject + image_list_str + "\nSee attached PDF for client submission details."

    logger.info("Sending email for Submission[%s]", submission.id)
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



def create_pdf(submission):
    """
    Returns a PDF file string.
    """
    answers = submission.answers
    questions = submission.questions

    # Get questions from sections
    fields = {}
    for section in questions:
        for form in section["forms"]:
            for field in form["fields"]:
                fs = field.get("fields", [field])
                for f in fs:
                    fields[f["name"]] = f

    answer_list = []
    for answer in answers:
        answer, name = answer.get("answer", ""), answer.get("name", "")
        field = fields[name]
        if field["type"] == "FILE":
            # Images are extracted elsewhere
            continue

        answer_list.append({
            "name": name,
            "prompt": field.get("prompt", ""),
            "answer": repr(answer),
        })
    
    pdb_html = render_to_string("client-intake.html", context={
        "answers": answer_list
    })
    return pdfkit.from_string(pdb_html, output_path=False, options=PDF_OPTIONS)


PDF_OPTIONS = {
    'quiet': True
    'page-size': 'Letter',
    'margin-top': '0.75in',
    'margin-right': '0.75in',
    'margin-bottom': '0.75in',
    'margin-left': '0.75in',
    'encoding': "UTF-8",
}
