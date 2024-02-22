import logging
from utils.sentry import sentry_task
from django.db import transaction
from django.conf import settings
from bs4 import BeautifulSoup

from core.models import Issue
from emails.utils.html import render_email_template
from emails.models import Email, EmailState
from emails.service.send import build_clerk_address
from office.closure.service import get_closure_email

logger = logging.getLogger(__name__)


@sentry_task
@transaction.atomic
def send_welcome_email(issue_pk: str):
    logging.info("Creating welcome email for Issue<%s>", issue_pk)
    issue = Issue.objects.select_related("client").get(pk=issue_pk)
    client = issue.client
    case_email = build_clerk_address(issue, email_only=True)
    name = client.get_full_name()

    html = get_email_html(name, issue.fileref, case_email)
    text = get_email_text(html)

    if (not settings.IS_PROD) and (not client.email.endswith("@anikalegal.com")):
        msg = "Not sending welcome email for Issue<%s> - only Anika emails allowed in non-prod environments"
        logging.error(msg, issue_pk)
    else:
        Email.objects.create(
            subject="Thanks for your enquiry",
            state=EmailState.READY_TO_SEND,
            from_address=build_clerk_address(issue),
            to_address=client.email,
            issue=issue,
            text=text,
            html=render_email_template(html),
        )
    # Mark request as sent
    Issue.objects.filter(pk=issue_pk).update(is_welcome_email_sent=True)


def get_email_html(name, fileref, case_email):
    html = get_closure_email()
    if not html:
        html = EMAIL_HTML
    return html.format(name=name, fileref=fileref, case_email=case_email)


def get_email_text(html):
    soup = BeautifulSoup(html, parser="lxml", features="lxml")
    text = soup.get_text("\n\n", strip=True)
    # The HTML version of the email uses an image as the sign-off name.
    # For the text version we just add a text sign-off.
    text += "\nAnika Legal"
    return text


EMAIL_HTML = """
<p>
Hi {name},
</p>
<p>
Thanks for submitting a case enquiry to Anika Legal.
<br/>
Your case number is {fileref}.
</p>
<p>
We’re reviewing your case and will aim to be in touch within the next week. We are operated by volunteers and appreciate your patience, as we find capacity to assign your matter.
</p>
<p>
Once a paralegal is assigned to your matter, they will email you to introduce themselves and organise a time to call you. Please note that any calls will appear from an unknown number.
</p>
<p>
If you have any questions in the meantime, or decide you no longer wish to proceed with our service, then you may reply to this email, or email us at the following address:
</p>
<p>
{case_email}
</p>
<p>
Kind regards,
</p>
"""
