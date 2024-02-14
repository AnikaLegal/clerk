import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker

from accounts.models import User
from core.models import Client, Issue, Person, Tenancy, IssueNote, FileUpload
from utils.signals import disable_signals, restore_signals

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Hide personal information"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        assert not settings.IS_PROD, "NEVER RUN THIS IN PROD!"
        disable_signals()
        fake = Faker()
        clients = Client.objects.all()
        issues = Issue.objects.all()
        people = Person.objects.all()
        tenancies = Tenancy.objects.all()
        notes = IssueNote.objects.exclude(note_type="EVENT")
        paralegals = (
            User.objects.filter(issue__isnull=False)
            .prefetch_related("issue_set")
            .distinct()
        )
        for t in tenancies:
            t.address = fake.street_address()
            t.suburb = fake.city()
            t.postcode = fake.postcode()
            t.save()

        for p in paralegals:
            p.email = fake.email()
            p.first_name = fake.first_name()
            p.last_name = fake.last_name()
            p.save()

        for p in people:
            p.full_name = fake.name()
            p.email = fake.email()
            p.address = fake.address()
            p.phone_number = fake.phone_number()
            p.save()

        for c in clients:
            c.first_name = fake.first_name()
            c.last_name = fake.last_name()
            c.email = fake.email()
            c.phone_number = fake.phone_number()
            c.save()

        for i in issues:
            if i.outcome_notes:
                i.outcome_notes = " ".join(fake.sentences())

            prefix = i.topic.upper()
            i.answers = {
                f"{prefix}_FOO": " ".join(fake.sentences()),
                f"{prefix}_BAR": " ".join(fake.sentences()),
                f"{prefix}_BAZ": " ".join(fake.sentences()),
            }
            i.save()

        for n in notes:
            n.text = " ".join(fake.sentences())
            n.save()

        # Replace uploaded files
        FileUpload.objects.update(file="file-uploads/do-your-best.png")

        restore_signals()
