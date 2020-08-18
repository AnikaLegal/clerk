import os

from django.core.management.base import BaseCommand

from actionstep.api import ActionstepAPI
from questions.models import Submission


class Command(BaseCommand):
    help = 'Map documents to users in Actionstep database'

    # Change this to the directory of the files
    base_dir = "./questions/management/commands/legacy_data"

    def upload(self, case_type, item):
        pass

    def handle(self, *args, **options):
        for case_type in os.listdir(self.base_dir):
            subpath = os.path.join(self.base_dir, case_type)
            for item in os.listdir(subpath):
                self.upload(case_type, item)