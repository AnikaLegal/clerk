import logging

from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker
from django.contrib.auth.models import User
from django.conf import settings

from utils.signals import disable_signals, restore_signals
from core.models import Issue, Client, Person, Tenancy

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Sync Actionstep paralegals to issues / users"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        assert settings.DEBUG, "NEVER RUN THIS IN PROD!"
        disable_signals()
        fake = Faker()
        clients = Client.objects.all()
        issues = Issue.objects.all()
        people = Person.objects.all()
        tenancies = Tenancy.objects.all()
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
            i.outcome_notes = fake.sentences()
            i.answers = {
                "FOO": " ".join(fake.sentences()),
                "BAR": " ".join(fake.sentences()),
                "BAZ": " ".join(fake.sentences()),
            }
            i.save()

        restore_signals()