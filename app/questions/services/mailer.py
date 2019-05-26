from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone


class Email:
    """
    Mail sending interface
    """

    def __init__(self, subject, recipients, from_email=settings.DEFAULT_FROM_EMAIL):
        self.subject = subject
        self.from_email = from_email
        self.recipients = recipients
        self.html_content = None
        self.text_content = None

    def with_text_body(self, text):
        """
        Add text body to the email - required.
        """
        self.text_content = text
        return self

    def with_text_template(self, template_name, template_context):
        """
        Add text body to the email via a template - required.
        """
        self.text_content = render_to_string(template_name, template_context)
        return self

    def with_html_template(self, template_name, template_context):
        """
        Add a HTML body to the email via a template - optional.
        """
        self.html_content = render_to_string(template_name, template_context)
        return self

    def send(self):
        """
        Send the email to the recipients
        """
        assert self.subject, "Cannot send mail, a subject is required"
        assert self.recipients, "Cannot send mail, no recipients"
        assert self.text_content, "Cannot send mail, a text body is required"
        email = EmailMultiAlternatives(
            subject=self.subject,
            body=self.text_content,
            from_email=self.from_email,
            to=self.recipients,
        )
        if self.html_content:
            email.attach_alternative(self.html_content, "text/html")

        email.send(fail_silently=False)
