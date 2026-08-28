import logging

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)

SUBJECT = "Your Anika Legal form - pick up where you left off"

BODY = """{greeting}

You started filling in a form with Anika Legal and asked us to send you a link
so you can finish it later.

Open this link on any device to pick up where you left off:

{url}

The link is just for you, so please don't share it.

If you didn't ask for this, you can ignore this email.

Anika Legal
"""


def get_greeting(answers: dict) -> str:
    """
    Greet the user by the name they asked to be called, falling back to their
    first name and then to no name at all - the form asks for the name well
    after the email address, so it is often not there yet.
    """
    name = (answers.get("PREFERRED_NAME") or answers.get("FIRST_NAME") or "").strip()
    return f"Hi {name}," if name else "Hi,"


def get_resume_url(submission) -> str:
    """
    The submission's own resume link, which the intake form reads the id from
    (see the SPA's /resume/ route).
    """
    return f"{settings.INTAKE_URL}resume/?sub={submission.id}"


def email_resume_link(submission) -> None:
    """
    Send the submission's resume link to the email address it holds, so the
    user can carry on from another device.
    """
    answers = submission.answers or {}
    email = answers.get("EMAIL")
    if not isinstance(email, str) or not email.strip():
        # The view turns the missing case into a 400 before reaching here, so
        # this only fires if that check is ever lost - better a loud failure
        # than mail addressed to nobody.
        raise ValueError(f"Submission[{submission.id}] holds no email address")
    body = BODY.format(
        greeting=get_greeting(answers), url=get_resume_url(submission)
    )
    send_mail(
        subject=SUBJECT,
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )
    logger.info("Sent resume link for Submission[%s]", submission.id)
