import hashlib
import json
from collections import namedtuple

from django.core.management.base import BaseCommand
from django.db import transaction
from emails.models import Email, EmailAttachment, EmailState, SharepointState

EmailData = namedtuple("EmailData", ["email", "attachments"])


class Command(BaseCommand):
    help = "Display and, potentially, remove duplicate received emails"

    def add_arguments(self, parser):
        parser.add_argument("fileref", type=str)
        parser.add_argument(
            "-d",
            "--delete",
            action="store_true",
            default=False,
            help="Actually remove duplicate emails instead of just displaying them.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        fileref = options["fileref"]
        delete = options["delete"]

        for thread in (
            Email.objects.filter(issue__fileref=fileref)
            .order_by("issue", "thread_name")
            .distinct("issue", "thread_name")
            .iterator()
        ):
            emails_by_hash: dict[str, list[EmailData]] = {}
            for email in (
                Email.objects.filter(
                    issue=thread.issue,
                    thread_name=thread.thread_name,
                    state=EmailState.INGESTED,
                )
                .order_by("created_at")
                .iterator()
            ):
                attachments = list(email.emailattachment_set.all().order_by("file"))
                data = EmailData(email=email, attachments=attachments)

                hash = self.get_hash_of_email_and_attachments(data)
                emails_by_hash.setdefault(hash, []).append(data)

            email_data_list: list[EmailData] = self.get_duplicate_email_data(
                emails_by_hash
            )
            self.handle_duplicate_email_data(thread, email_data_list, delete)

    def get_hash_of_email_and_attachments(self, data: EmailData) -> str:
        m = hashlib.sha256()
        received_data = json.dumps(data.email.received_data, sort_keys=True)
        m.update(received_data.encode())

        # Email attachments contain a hash of the file contents in the
        # file path so we only have to update the hash with the file
        # path to detect changes to the file contents.
        for attachment in data.attachments:
            if attachment.file:
                m.update(attachment.file.name.encode())

        return m.hexdigest()

    def get_duplicate_email_data(
        self, emails_by_hash: dict[str, list[EmailData]]
    ) -> list[EmailData]:
        return [
            email_data
            for email_data_list in emails_by_hash.values()
            for email_data in email_data_list
            if len(email_data_list) > 1
        ]

    def handle_duplicate_email_data(
        self, thread: Email, email_data_list: list[EmailData], delete: bool
    ):
        if not email_data_list:
            self.stdout.write(
                f"No duplicate messages found in thread '{thread.thread_name}'"
            )
        else:
            self.stdout.write(
                f"Found {len(email_data_list)} duplicate messages in thread '{thread.thread_name}':"
            )

            retain_email = self.get_email_to_retain(email_data_list)
            if not retain_email:
                raise Exception("Logic error: expected to find an email to retain")

            for email_data in email_data_list:
                email = email_data.email
                attachment_count = len(email_data.attachments)
                uploaded_count = self.get_uploaded_attachment_count(
                    email_data.attachments
                )
                is_retained = retain_email.email.pk == email.pk
                delete_text = "DELETED" if delete else "TO BE DELETED"
                keep_text = "KEPT" if delete else "TO BE KEPT"

                self.stdout.write(
                    f"- {email.pk} - {email.thread_name} - {email.created_at} "
                    f"- {attachment_count} attachments - {uploaded_count} uploaded"
                    f" - {delete_text if not is_retained else keep_text}"
                )
                if delete and not is_retained:
                    email.delete()

    def get_uploaded_attachment_count(self, attachments: list[EmailAttachment]) -> int:
        return len(
            [a for a in attachments if a.sharepoint_state == SharepointState.UPLOADED]
        )

    def get_email_to_retain(self, email_data_list: list[EmailData]) -> EmailData | None:
        # Retain the email with the most uploaded attachments or, if there are
        # no uploaded attachments, the oldest creation date.
        return min(
            email_data_list,
            key=lambda email_data: (
                -self.get_uploaded_attachment_count(email_data.attachments),
                email_data.email.created_at,
            ),
            default=None,
        )
