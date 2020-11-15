import logging

from django.core.management.base import BaseCommand

from core.models import Issue
from actionstep.api import ActionstepAPI


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Sync action step file ids to issues"

    def handle(self, *args, **kwargs):
        api = ActionstepAPI()

        for issue in Issue.objects.filter(is_submitted=True).all():
            # Check if this issue already has an action

            logger.info("Checking fileref for Issue<%s>", issue.id)
            action_id = None
            issue_filenotes = api.filenotes.list_by_text_match(issue.pk)
            if issue_filenotes:
                action_id = max([int(fn["links"]["action"]) for fn in issue_filenotes])

            if action_id:
                # An matter has already been created for this issue
                logger.info("Found existing matter %s for %s", action_id, issue.pk)
                action_data = api.actions.get(action_id)
                fileref_name = action_data["reference"]
                logger.info("Setting fileref %s for Issue<%s>", fileref_name, issue.pk)
                Issue.objects.filter(pk=issue.pk).update(fileref=fileref_name)
            else:
                logger.info("Found existing matter %s for %s", action_id, issue.pk)
