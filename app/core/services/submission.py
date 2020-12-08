from datetime import datetime
import logging

from django.db import transaction
from django.db.models.expressions import Case
from django.utils import timezone

from core.models import Submission, Issue, Client, Person, FileUpload, Tenancy
from core.models.issue import CaseTopic
from questions.management.commands.migrate_core import CALL_TIMES

logger = logging.getLogger(__name__)


@transaction.atomic
def process_submission(sub_pk: str):
    """
    Convert a client's intake form submission into more meaningful relational objects:
        - Client: the client
        - Issue: the client's issues
        - FileUpload: files associated with an issue
        - Person: landlords and agents
        - Tenancy: the client's home

    """
    logger.info("Processing Submission[%s]", sub_pk)
    sub = Submission.objects.get(pk=sub_pk)
    answers = sub.answers

    logger.info("Processing Client for Submission[%s]", sub_pk)
    try:
        referrer = None
        referrer = answers.get("LEGAL_CENTER_REFERRER") or referrer
        referrer = answers.get("HOUSING_SERVICE_REFERRER") or referrer
        referrer = answers.get("CHARITY_REFERRER") or referrer
        referrer = answers.get("SOCIAL_REFERRER") or referrer
        client, _ = Client.objects.get_or_create(
            email=answers["EMAIL"],
            defaults={
                "first_name": answers["FIRST_NAME"],
                "last_name": answers["LAST_NAME"],
                "date_of_birth": parse_date_string(answers["DOB"]),
                "phone_number": answers["PHONE"],
                "call_time": answers["AVAILIBILITY"] or "",
                "referrer_type": answers["REFERRER_TYPE"] or "",
                "referrer": referrer or "",
                "gender": answers["GENDER"],
                "gender_details": answers.get("GENDER_DETAILS"),
                "can_speak_non_english": answers["CAN_SPEAK_NON_ENGLISH"],
                "is_aboriginal_or_torres_strait_islander": answers[
                    "IS_ABORIGINAL_OR_TORRES_STRAIT_ISLANDER"
                ],
            },
        )
        logger.info("Processed Client[%s] for Submission[%s]", client.pk, sub_pk)
    except Exception:
        logger.exception("Could not process Client for Submission[%s]")
        raise

    logger.info("Processing Tenancy for Submission[%s]", sub_pk)
    try:
        agent = None
        landlord = None
        if answers["PROPERTY_MANAGER_IS_AGENT"]:
            agent = Person.objects.create(
                full_name=answers["AGENT_NAME"].title(),
                address=answers["AGENT_ADDRESS"],
                email=answers["AGENT_EMAIL"],
                phone_number=answers["AGENT_PHONE"],
            )

        if answers["LANDLORD_NAME"]:
            landlord = Person.objects.create(
                full_name=answers["LANDLORD_NAME"].title(),
                address=answers.get("LANDLORD_ADDRESS") or "",
                email=answers.get("LANDLORD_EMAIL") or "",
                phone_number=answers.get("LANDLORD_PHONE") or "",
            )

        tenancy, _ = Tenancy.objects.get_or_create(
            address=answers["ADDRESS"],
            client=client,
            defaults={
                "is_on_lease": answers["IS_ON_LEASE"],
                "started": parse_date_string(answers["START_DATE"]),
                "landlord": landlord,
                "agent": agent,
                "postcode": answers["POSTCODE"],
                "suburb": answers["SUBURB"],
            },
        )
        logger.info("Processed Tenancy[%s] for Submission[%s]", tenancy.pk, sub_pk)
    except Exception:
        logger.exception("Could not process Tenancy for Submission[%s]")
        raise

    ISSUE_ANSWERS = {
        "REPAIRS": {
            "non_photo": [
                "REPAIRS_REQUIRED",
                "REPAIRS_ISSUE_DESCRIPTION",
                "REPAIRS_ISSUE_START",
            ],
            "photo": ["REPAIRS_ISSUE_PHOTO"],
        },
        "RENT_REDUCTION": {
            "non_photo": [
                "RENT_REDUCTION_ISSUES",
                "RENT_REDUCTION_ISSUE_DESCRIPTION",
                "RENT_REDUCTION_ISSUE_START",
                "RENT_REDUCTION_IS_NOTICE_TO_VACATE",
            ],
            "photo": [
                "RENT_REDUCTION_ISSUE_PHOTO",
                "RENT_REDUCTION_NOTICE_TO_VACATE_DOCUMENT",
            ],
        },
        "OTHER": {
            "non_photo": ["OTHER_ISSUE_DESCRIPTION"],
            "photo": [],
        },
    }
    for topic in answers["ISSUES"]:
        logger.info("Processing %s Issue for Submission[%s]", topic, sub_pk)
        try:
            non_photo_answers = ISSUE_ANSWERS[topic]["non_photo"]
            photo_answers = ISSUE_ANSWERS[topic]["photo"]
            issue_answers = {k: answers[k] for k in non_photo_answers}
            issue_upload_ids = []
            for k in photo_answers:
                issue_upload_ids += [f["id"] for f in (answers.get(k) or [])]

            issue = Issue.objects.create(
                topic=topic,
                answers=issue_answers,
                client=client,
            )
            FileUpload.objects.filter(pk__in=issue_upload_ids).update(issue=issue.pk)
            logger.info(
                "Processed %s Issue[%s] for Submission[%s]", topic, issue.pk, sub_pk
            )
        except Exception:
            logger.exception(
                "Could not process %s Issue for Submission[%s]", topic, sub_pk
            )
            raise

    Submission.objects.filter(pk=sub.pk).update(is_processed=True)


def parse_date_string(s: str):
    # 1995-6-6
    dt = datetime.strptime(s, "%Y-%d-%M")
    tz = timezone.get_current_timezone()
    dt = timezone.make_aware(dt, timezone=tz)
    return dt.replace(hour=0, minute=0)
