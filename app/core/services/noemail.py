import logging
from datetime import datetime

from django.db import transaction
from django.utils import timezone

from core.models import NoEmailAdmin
from emails.models import NoEmail

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
        noemail, _ = NoEmail.objects.get_or_create(
            name=answers["name"],
            phone_number=answers["phone_number"],
        )
        logger.info("Processed NoEmail[%s] for Submission[%s]", noemail.pk, sub_pk)
    except Exception:
        logger.exception("Could not process NoEmail for Submission[%s]")
        raise

    NoEmailAdmin.objects.filter(pk=sub_pk).update(is_processed=True)
