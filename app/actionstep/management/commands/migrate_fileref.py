import logging

from django.core.management.base import BaseCommand

from actionstep.api import ActionstepAPI, participants
from core.models import Issue

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Sync action step file ids to issues"

    def handle(self, *args, **kwargs):
        api = ActionstepAPI()
        actions = api.actions.list()

        for issue in Issue.objects.select_related("client").all():
            # Check if this issue already has an action
            if issue.fileref:
                logger.info("Issue<%s> already has fileref %s", issue.id, issue.fileref)
                continue

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
                Issue.objects.filter(pk=issue.pk).update(
                    fileref=fileref_name, is_case_sent=True
                )
            else:
                logger.info(
                    "Could not find a matter Issue<%s> based on pk, trying client email.",
                    issue.pk,
                )
                client = issue.client
                participant = api.participants.get_by_email(client.email)
                if participant:
                    participant_id = str(participant["id"])
                    participant_actions = [
                        a
                        for a in actions
                        if participant_id in a["links"]["primaryParticipants"]
                    ]
                    assert (
                        len(participant_actions) < 2
                        or participant_actions[0]["reference"] == "C0075"
                    )
                    if participant_actions:
                        action_data = participant_actions[0]
                        logger.info(
                            "Found existing matter %s for %s",
                            action_data["id"],
                            issue.pk,
                        )
                        fileref_name = action_data["reference"]
                        logger.info(
                            "Setting fileref %s for Issue<%s>", fileref_name, issue.pk
                        )
                        Issue.objects.filter(pk=issue.pk).update(
                            fileref=fileref_name, is_case_sent=True
                        )
                    else:
                        logger.info(
                            "Could not find a matter Issue<%s> based on participant.",
                            issue.pk,
                        )
                else:
                    logger.info(
                        "Could not find a matter Issue<%s> based on participant.",
                        issue.pk,
                    )
