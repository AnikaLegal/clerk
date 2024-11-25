import logging
from random import randint

from accounts.models import CaseGroups, User
from core.models import Client, FileUpload, Issue, IssueNote, Person, Service, Tenancy
from core.models.issue_note import NoteType
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q
from emails.models import Email, EmailAttachment
from mimesis import Generic
from mimesis.locales import Locale
from utils.signals import disable_signals, restore_signals

logger = logging.getLogger(__name__)
generic = Generic(locale=Locale.EN_AU)
email_domains = ["example.com", "example.org", "example.edu"]


class Command(BaseCommand):
    help = "Hide personal information"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        assert not settings.IS_PROD, "NEVER RUN THIS IN PROD!"
        self.stdout.write("\nObfuscating personal information...")
        disable_signals()

        clients = Client.objects.all()
        emails = Email.objects.all()
        issues = Issue.objects.all()
        notes = IssueNote.objects.exclude(note_type=NoteType.EVENT)
        people = Person.objects.all()
        services = Service.objects.all()
        tenancies = Tenancy.objects.all()

        # Obfuscate any user that isn't a lawyer, admin or superuser. We want to
        # keep the accounts unchanged for users in those groups so they can be
        # used for testing.
        users = User.objects.exclude(
            Q(groups__name__in=[CaseGroups.LAWYER, CaseGroups.ADMIN])
            | Q(email="dummy.test@anikalegal.com")
            | Q(is_superuser=True)
        ).distinct()

        for t in tenancies:
            t.address = generic.address.address()
            t.suburb = generic.address.city()
            t.postcode = generic.address.postal_code()
            t.save()

        for u in users:
            u.email = generic.person.email(domains=email_domains, unique=True)
            u.username = u.email  # Username same as fake email.
            u.first_name = generic.person.first_name()
            u.last_name = generic.person.last_name()
            u.save()

        for p in people:
            p.full_name = generic.person.full_name()
            p.email = generic.person.email(domains=email_domains)
            p.phone_number = generic.person.phone_number()
            p.address = generic.address.address()
            p.save()

        for c in clients:
            c.first_name = generic.person.first_name()
            c.last_name = generic.person.last_name()
            if c.preferred_name:
                c.preferred_name = generic.person.first_name()
            c.email = generic.person.email(domains=email_domains)
            c.phone_number = generic.person.phone_number()
            c.save()

        for i in issues:
            if i.outcome_notes:
                i.outcome_notes = generic.text.text(quantity=2)

            prefix = i.topic.upper()
            i.answers = {
                f"{prefix}_FOO": generic.text.text(quantity=3),
                f"{prefix}_BAR": generic.text.text(quantity=3),
                f"{prefix}_BAZ": generic.text.text(quantity=3),
            }
            i.save()

        for n in notes:
            n.text = generic.text.text(quantity=3)
            n.save()

        for e in emails:
            e.received_data = None
            e.subject = generic.text.title()
            e.text = generic.text.text(quantity=randint(1, 10))
            e.html = ""

            # This could be smarter and attempt to match the sender related user
            # or the client with the to/from address and use the same obfuscated
            # email but it's unclear if that is actually useful.
            if e.from_address:
                e.from_address = generic.person.email(domains=email_domains)
            if e.to_address:
                e.to_address = generic.person.email(domains=email_domains)
            e.cc_addresses = [
                generic.person.email(domains=email_domains) for _ in e.cc_addresses
            ]
            e.save()

        for s in services:
            if s.notes:
                s.notes = generic.text.sentence()
                s.save()

        # Replace files attached to emails
        EmailAttachment.objects.update(
            file="email-attachments/do-your-best.png", content_type="image/png"
        )

        # Replace uploaded files
        FileUpload.objects.update(file="file-uploads/do-your-best.png")

        restore_signals()
