from django.core.management.base import BaseCommand

from core.models import Issue
from actionstep.services.pdf import create_pdf


class Command(BaseCommand):
    help = "Create PDF for Issue"

    def add_arguments(self, parser):
        parser.add_argument("issue_pk", type=str, help="Issue PK")

    def handle(self, *args, **kwargs):
        issue_pk = kwargs["issue_pk"]
        issue = Issue.objects.get(pk=issue_pk)
        pdf_bytes = create_pdf(issue)
        fname = f"test-{issue_pk}.pdf"
        with open(fname, "wb") as f:
            f.write(pdf_bytes)
