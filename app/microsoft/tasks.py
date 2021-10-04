import logging

from core.models import Issue
from utils.sentry import WithSentryCapture
from .service import set_up_new_case


logger = logging.getLogger(__name__)


def _set_up_new_case_task(issue_pk: str):
    logger.info("Setting up folder on Sharepoint for Issue<%s>", issue_pk)
    issue = Issue.objects.get(pk=issue_pk)
    set_up_new_case(issue)
    Issue.objects.filter(pk=issue_pk).update(is_sharepoint_set_up=True)
    logger.info("Finished setting up folder on Sharepoint for Issue<%s>", issue_pk)


set_up_new_case_task = WithSentryCapture(_set_up_new_case_task)
