from django.core.management.base import BaseCommand

from questions.models import Submission
from questions.services.submission import create_pdf


class Command(BaseCommand):
    help = "Create PDF from Submission"

    def add_arguments(self, parser):
        parser.add_argument("submission_pk", type=str, help="Submission PK")

    def handle(self, *args, **kwargs):
        submission_pk = kwargs["submission_pk"]
        submission = Submission.objects.get(pk=submission_pk)
        pdf_bytes = create_pdf(submission)
        fname = f"test-{submission_pk}.pdf"
        with open(fname, "wb") as f:
            f.write(pdf_bytes)
