from core.models import Issue
from django.core.management.base import BaseCommand
from microsoft.service import set_up_new_case


class Command(BaseCommand):
    help = "Create the relevant documents based on the document templates for the topic of the supplied case(s)"

    def add_arguments(self, parser):
        parser.add_argument("fileref", nargs="+", type=str)

    def handle(self, *args, **kwargs):
        for issue in Issue.objects.filter(fileref__in=kwargs["fileref"]):
            set_up_new_case(issue)
