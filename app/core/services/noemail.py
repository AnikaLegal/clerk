import logging
from datetime import datetime

from django.db import transaction
from django.utils import timezone

from emails.admin import NoEmailAdmin

logger = logging.getLogger(__name__)


@transaction.atomic
def process_noemail(sub_pk: str):
    """
    Convert a client's noemail submission
    """

    logger.info("Processing Submission[%s]", sub_pk)
    sub = NoEmailAdmin.objects.get(pk=sub_pk)
    answers = sub.answers

    try:
        info, _ = NoEmailAdmin.objects.get_or_create(
            name = answers.get("name"),
            phone_number = answers.get("phone_number"),
        )
        logger.info("Processed Tenancy[%s] for Submission[%s]", info.pk, sub_pk)
    except Exception:
        logger.exception("Could not process Tenancy for Submission[%s]")
        raise

    NoEmailAdmin.objects.filter(pk=sub_pk).update(is_processed=True)
