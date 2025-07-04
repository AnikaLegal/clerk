import logging
import os
from io import BytesIO

from accounts.models import CaseGroups, User
from core.models import Client, FileUpload, Issue, IssueNote, Person, Service, Tenancy
from core.models.issue_note import NoteType
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q
from emails.models import Email, EmailAttachment
from faker import Faker
from utils.signals import disable_signals, restore_signals

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Hide personal information"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        assert not settings.IS_PROD, "NEVER RUN THIS IN PROD!"
        self.stdout.write("\nObfuscating personal information...")
        disable_signals()

        fake = Faker("en_AU")

        clients = Client.objects.all()
        emails = Email.objects.all()
        issues = Issue.objects.all()
        notes = IssueNote.objects.exclude(note_type=NoteType.EVENT)
        people = Person.objects.all()
        services = Service.objects.all()
        tenancies = Tenancy.objects.all()

        # Obfuscate any user that isn't an admin or superuser. We want to keep
        # the accounts unchanged for users in those groups so they can be used
        # for testing. Also keep the coordinators account.
        users = User.objects.exclude(
            Q(groups__name__in=[CaseGroups.ADMIN])
            | Q(is_superuser=True)
            | Q(email="coordinators@anikalegal.com")
        ).distinct()

        for t in tenancies.iterator():
            t.address = fake.street_address()
            t.suburb = fake.city()
            t.postcode = fake.postcode()
            t.save()

        for u in users.iterator():
            u.email = fake.unique.email()
            u.username = u.email  # Username same as fake email.
            u.first_name = fake.first_name()
            u.last_name = fake.last_name()
            u.save()

        for p in people.iterator():
            p.full_name = fake.name()
            p.email = fake.email()
            p.address = fake.address()
            p.phone_number = fake.phone_number()
            p.save()

        for c in clients.iterator():
            c.first_name = fake.first_name()
            c.last_name = fake.last_name()
            if c.preferred_name:
                c.preferred_name = fake.first_name()
            c.email = fake.email()
            c.phone_number = fake.phone_number()
            c.save()

        for i in issues.iterator():
            if i.outcome_notes:
                i.outcome_notes = " ".join(fake.sentences())

            # Redact the answers to issue-specific intake form questions.
            redacted_text = "[REDACTED]"
            redacted_answers = {}
            for key, value in i.answers.items():
                if value is not None:
                    value = (
                        [redacted_text] * len(value)
                        if isinstance(value, list)
                        else redacted_text
                    )
                redacted_answers[key] = value
            i.answers = redacted_answers

            i.save()

        for n in notes.iterator():
            n.text = " ".join(fake.sentences())
            n.save()

        for e in emails.iterator():
            e.received_data = None
            e.subject = fake.sentence()
            e.text = "\n\n".join(fake.paragraphs())
            e.html = ""

            # This could be smarter and attempt to match the sender related user
            # or the client with the to/from address and use the same obfuscated
            # email but it's unclear if that is actually useful.
            if e.from_address:
                e.from_address = fake.email()
            if e.to_address:
                e.to_address = fake.email()
            e.cc_addresses = [fake.email() for _ in e.cc_addresses]
            e.save()

        for s in services.iterator():
            if s.notes:
                s.notes = " ".join(fake.sentences())
                s.save()

        # Save sample files to storage (AWS S3) to use for email attachments &
        # uploaded files.
        file_name = "sample.pdf"
        email_attachment = os.path.join(EmailAttachment.UPLOAD_KEY, file_name)
        file_upload = os.path.join(FileUpload.UPLOAD_KEY, file_name)

        bytes = fake.image(image_format="pdf")
        default_storage.save(email_attachment, BytesIO(bytes))
        default_storage.save(file_upload, BytesIO(bytes))

        # Replace files attached to emails.
        EmailAttachment.objects.update(
            file=email_attachment, content_type="application/pdf"
        )

        # Replace uploaded files.
        FileUpload.objects.update(file=file_upload)

        restore_signals()
