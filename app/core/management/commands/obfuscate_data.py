import logging
import os
from io import BytesIO

from accounts.models import CaseGroups, User
from auditlog.context import disable_auditlog
from auditlog.models import LogEntry
from core.models import (
    AuditEvent,
    Client,
    FileUpload,
    Issue,
    IssueDate,
    IssueNote,
    Person,
    Service,
    Submission,
    Tenancy,
)
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

fake = Faker("en_AU")
email_addresses = dict()


class Command(BaseCommand):
    help = "Hide personal information"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        assert not settings.IS_PROD, "NEVER RUN THIS IN PROD!"
        self.stdout.write("\nObfuscating personal information...")
        disable_signals()

        email_addresses = dict()

        clients = Client.objects.all()
        emails = Email.objects.all()
        issues = Issue.objects.all()
        notes = IssueNote.objects.exclude(note_type=NoteType.EVENT)
        dates = IssueDate.objects.all()
        people = Person.objects.all()
        services = Service.objects.all()
        tenancies = Tenancy.objects.all()
        audit_events = AuditEvent.objects.all()
        log_entries = LogEntry.objects.all()
        submissions = Submission.objects.all()

        # Obfuscate any user that isn't an admin or superuser. We want to keep
        # the accounts unchanged for users in those groups so they can be used
        # for testing. Also keep the coordinators account.
        users = User.objects.exclude(
            Q(groups__name__in=[CaseGroups.ADMIN])
            | Q(is_superuser=True)
            | Q(email="coordinators@anikalegal.com")
        ).distinct()

        for t in tenancies.iterator():
            if t.address:
                t.address = fake.street_address()
            if t.suburb:
                t.suburb = fake.city()
            if t.postcode:
                t.postcode = fake.postcode()
            t.save()

        for u in users.iterator():
            u.email = get_email(u.email)
            u.username = u.email  # Username same as fake email.
            u.first_name = fake.first_name()
            u.last_name = fake.last_name()
            u.save()

        for p in people.iterator():
            if p.full_name:
                p.full_name = fake.name()
            if p.email:
                p.email = get_email(p.email)
            if p.address:
                p.address = fake.address()
            if p.phone_number:
                p.phone_number = fake.phone_number()
            p.save()

        for c in clients.iterator():
            if c.first_name:
                c.first_name = fake.first_name()
            if c.last_name:
                c.last_name = fake.last_name()
            if c.preferred_name:
                c.preferred_name = fake.first_name()
            if c.email:
                c.email = get_email(c.email)
            if c.phone_number:
                c.phone_number = fake.phone_number()
            if c.contact_notes:
                c.contact_notes = " ".join(fake.sentences())
            c.save()

        for i in issues.iterator():
            if i.outcome_notes:
                i.outcome_notes = " ".join(fake.sentences())

            # Redact the answers to issue-specific intake form questions.
            if i.answers:
                i.answers = get_redacted_answers(i.answers)

            i.save()

        for n in notes.iterator():
            n.text = " ".join(fake.sentences())
            n.save()

        # Emails are grouped by subject (normalised in the thread_name field).
        # We want to keep the same grouping when we obfuscate them so we attempt
        # to use the same obfuscated subject for all emails in the same group.
        for thread in (
            emails.order_by("issue", "thread_name")
            .distinct("issue", "thread_name")
            .iterator()
        ):
            thread_subject = fake.sentence()

            for e in emails.filter(
                issue=thread.issue, thread_name=thread.thread_name
            ).iterator():
                e.subject = thread_subject
                e.received_data = None
                e.text = "\n\n".join(fake.paragraphs())
                e.html = ""

                if e.from_address:
                    e.from_address = get_email(e.from_address)
                if e.to_address:
                    e.to_address = get_email(e.to_address)
                e.cc_addresses = [get_email(addr) for addr in e.cc_addresses]
                e.save()

        for s in services.iterator():
            if s.notes:
                s.notes = " ".join(fake.sentences())
                s.save()

        with disable_auditlog():
            for d in dates.iterator():
                if d.notes:
                    d.notes = " ".join(fake.sentences())
                    d.save()

        # We just delete audit events and log entries as it's too fiddly to
        # update them with obfuscated data.
        audit_events.delete()
        log_entries.delete()

        # Remove all answers from submissions as they contain personal info.
        for s in submissions.iterator():
            if s.answers:
                s.answers = get_redacted_answers(s.answers)
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


def get_email(email: str) -> str:
    email = email.lower()
    if email not in email_addresses:
        email_addresses[email] = fake.unique.email()
    return email_addresses[email]


def get_redacted_answers(answers: dict) -> dict:
    redacted_text = "[REDACTED]"
    redacted_answers = {}
    for key, value in answers.items():
        if value is not None:
            if key == "EMAIL" or key == "CLIENT_EMAIL":
                # Keep email addresses consistent with other
                # obfuscated emails.
                value = get_email(value)
            else:
                value = (
                    [redacted_text] * len(value)
                    if isinstance(value, list)
                    else redacted_text
                )
        redacted_answers[key] = value
    return redacted_answers
