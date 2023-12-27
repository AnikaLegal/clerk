import re

from django.utils.text import slugify
from emails.models import Email


class EmailThread:
    def __init__(self, email: Email):
        self.emails = [email]
        self.issue = email.issue
        self.subject = email.subject or "No Subject"
        self.slug = self.slugify_subject(self.subject)
        self.most_recent = email.created_at

    @staticmethod
    def slugify_subject(subject):
        sub = subject or ""
        sub_cleaned = re.sub(r"re\s*:\s*", "", sub, flags=re.IGNORECASE)
        sub_cleaned = sub_cleaned or "No Subject"
        return slugify(sub_cleaned)

    def is_email_in_thread(self, email: Email) -> bool:
        return self.slug == self.slugify_subject(email.subject)

    def add_email_if_in_thread(self, email: Email) -> bool:
        is_in_thread = self.is_email_in_thread(email)
        if is_in_thread:
            self.emails.append(email)
            if email.created_at > self.most_recent:
                self.most_recent = email.created_at

        return is_in_thread

    def __repr__(self):
        return f"EmailThread<{self.subject}>"
