import json
import logging
from email.utils import getaddresses

from core.models.issue import CaseStage, Issue
from core.models.issue_note import IssueNote, NoteType
from django.conf import settings
from django.db import transaction
from django.db.models import Q, QuerySet
from django.utils import timezone
from django.utils.datastructures import MultiValueDict
from emails.models import (
    DuplicateEmailDataError,
    Email,
    EmailAttachment,
    EmailState,
)
from utils.sentry import sentry_task
from .send import build_clerk_address


logger = logging.getLogger(__name__)


EMAIL_RECEIVE_RULES = (
    (
        lambda e: e.state in [EmailState.RECEIVED, EmailState.INGEST_FAILURE],
        "not in 'received' or 'failure' state.",
    ),
)


def save_inbound_email(data: MultiValueDict, files: MultiValueDict) -> bool:
    """
    Parse inbound email and attachment data from SendGrid and save to the database.

    Some ESPs impose strict time limits on webhooks, and will consider them
    failed if they don't respond within a certain timeframe. We have to have a
    mechanism to prevent adding duplicate emails when SendGrid resends the email
    data after a timeout because we haven't finished processing it.

    ### Parameters
        1. data: data in SendGrid inbound parse default (i.e. not raw) format.
        2. files: Django file upload objects for the files attached to the email.

    ### Returns
        A boolean indicating whether the email and all attachments have been
        successfully saved to the database.

    ### See
        - https://www.twilio.com/docs/sendgrid/for-developers/parsing-email/setting-up-the-inbound-parse-webhook#default-parameters
        - https://docs.djangoproject.com/en/5.2/topics/http/file-uploads/
    """

    logger.info("Saving inbound email data")
    try:
        email = Email.objects.create(received_data=data, state=EmailState.SAVING)  # ty:ignore[unresolved-attribute]
    except DuplicateEmailDataError as e:
        # We need to figure out if we are still saving the email and attachments
        # so we can respond appropriately back to SendGrid. Note that we
        # indicate that we haven't successfully saved to the database if the
        # save is still in progress so we can get SendGrid to resend in case
        # something goes wrong before we finish.
        is_saved = (
            Email.objects.filter(received_data_hash=e.hash)  # ty:ignore[unresolved-attribute]
            .exclude(state=EmailState.SAVING)
            .exists()
        )
        logger.info(f"{str(e)} - finished saving? {is_saved}")
        return is_saved

    logger.info(f"Saved inbound email data, hash: {email.received_data_hash}")

    with transaction.atomic():
        try:
            for file in files.values():
                EmailAttachment.objects.create(  # ty:ignore[unresolved-attribute]
                    email=email, file=file, content_type=file.content_type
                )
            email.state = EmailState.RECEIVED
            email.save()
        except Exception:
            # Remove the email instance we created so that we can retry when
            # SendGrid sends the email again.
            email.delete()
            raise

    logger.info(f"Finished saving inbound email, hash: {email.received_data_hash}")
    return True


@sentry_task
def ingest_email_task(email_pk: int):
    """
    Ingests a received email and attempts to associate it with a case.
    """
    email = Email.objects.get(pk=email_pk)  # ty:ignore[unresolved-attribute]
    for rule, msg in EMAIL_RECEIVE_RULES:
        if not rule(email):
            logger.error(f"Cannot ingest Email[{email_pk}]: {msg}")
            return

    try:
        if not email.received_data:
            raise Exception("No received data to parse")

        parsed_data = parse_received_data(email.received_data)

        with transaction.atomic():
            email.state = EmailState.INGESTED
            email.issue = parsed_data["issue"]
            email.from_address = parsed_data["from_address"]
            email.to_address = parsed_data["to_address"]
            email.cc_addresses = parsed_data["cc_addresses"]
            email.subject = parsed_data["subject"]
            email.text = parsed_data["text"]
            email.html = parsed_data["html"]
            email.processed_at = timezone.now()
            email.save()

            IssueNote.objects.create(  # ty:ignore[unresolved-attribute]
                note_type=NoteType.EMAIL,
                content_object=email,
                issue=email.issue,
                created_at=email.created_at,
                text=email.get_received_note_text(),
            )
    except Exception:
        logger.exception(f"Error ingesting Email[{email_pk}]")
        email.state = EmailState.INGEST_FAILURE
        email.save()


def parse_received_data(email_data: dict) -> dict:
    """
    Returns the parsed email data as a dict or None
    data is in format: {
        subject: str
        text: str
        from_address: str
        to_address: str
        cc_addresses: List[str],
        issue: Issue
    }
    """
    parsed_data = {}
    # Find who the email is to.
    envelope = json.loads(email_data["envelope"])
    to_addrs = [addr for _, addr in getaddresses(envelope["to"])]
    if not to_addrs:
        raise Exception("No 'to' addresses found")

    local_to_addrs = [addr for addr in to_addrs if is_inbound_email_domain(addr)]
    if not local_to_addrs:
        raise Exception(f"No local 'to' addresses found: {to_addrs}")

    issues = get_issues_from_addresses(local_to_addrs)
    if issues.count() == 0:
        raise Exception(f"No issues found for 'to' addresses: {local_to_addrs}")
    elif issues.count() == 1:
        issue = issues.first()
    else:
        # The email has been sent to multiple local addresses associated with
        # different issues. Select the latest open issue otherwise just the
        # latest issue. Also emit a warning.
        # NOTE: We could remove this if we separated the saving of received data
        # from our ESP from the creation of the email record. We could then
        # create an email record for each local "to" address and associate it
        # with the relevant issue.
        issue = issues.exclude(stage=CaseStage.CLOSED).order_by("-created_at").first()
        if not issue:
            issue = issues.order_by("-created_at").first()

        logger.warning(
            "Multiple issues found for 'to' addresses %s, selecting Issue pk=%s, stage=%s, created_at=%s",
            local_to_addrs,
            issue.pk,
            issue.stage,
            issue.created_at,
        )

    # NOTE: We use the "canonical" clerk email address as the "to" address because:
    # - It's easier to determine from the issue when there are multiple local
    #   "to" addresses.
    # - It uses the correct domain for emails sent to the legacy domain which we
    #   have to continue accepting for now.
    parsed_data["to_address"] = build_clerk_address(issue, True)
    parsed_data["from_address"] = envelope["from"]

    cc_addr_strs = email_data.get("cc", "")
    to_addr_strs = email_data["to"]

    parsed_addrs = getaddresses([cc_addr_strs] + [to_addr_strs])
    cc_addrs = [
        email
        for _, email in parsed_addrs
        if email != ""
        and email not in local_to_addrs
        and email != parsed_data["to_address"]
    ]

    parsed_data["cc_addresses"] = list(dict.fromkeys(cc_addrs))
    parsed_data["text"] = email_data.get("text", "")
    parsed_data["subject"] = email_data["subject"]
    parsed_data["html"] = email_data.get("html", "")
    parsed_data["issue"] = issue

    return parsed_data


def get_issues_from_addresses(addresses: list[str]) -> QuerySet[Issue]:
    query = Q()
    for address in addresses:
        user, _ = address.split("@")
        user_parts = user.split(".")
        issue_prefix = user_parts[-1]
        query |= Q(id__startswith=issue_prefix)

    return Issue.objects.filter(query)  # ty:ignore[unresolved-attribute]


def is_inbound_email_domain(email_addr: str) -> bool:
    _, domain = email_addr.split("@")

    # TODO: We have to accept emails from our the old mail domain for a while
    # until all open cases from before the domain change are closed. Remove the
    # legacy domain check when possible.
    return domain == settings.EMAIL_DOMAIN or (
        settings.EMAIL_DOMAIN_LEGACY is not None
        and domain == settings.EMAIL_DOMAIN_LEGACY
    )
